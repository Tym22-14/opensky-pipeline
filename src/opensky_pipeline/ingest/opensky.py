from datetime import UTC, datetime
from typing import Any

import httpx

from opensky_pipeline.config import settings
from opensky_pipeline.exceptions import APIError, RateLimitError
from opensky_pipeline.ingest.auth import TokenManager
from opensky_pipeline.ingest.models import StateVectorsResponse
from opensky_pipeline.logging import get_logger
from opensky_pipeline.storage.s3 import S3Storage

logger = get_logger(__name__)


class OpenSkyStateVectorsIngestor:
    """
    Fetches state vectors from OpenSky API and writes to MinIO as Parquet.

    Responsibilities:
    - authenticate via TokenManager
    - fetch state vectors for configured bounding box
    - parse and validate via Pydantic models
    - write partitioned Parquet to S3 raw layer
    """

    def __init__(self) -> None:
        self._token_manager = TokenManager()
        self._storage = S3Storage()

    def fetch_and_store(self) -> int:
        """
        Fetch current state vectors and persist to raw layer.
        Returns number of records written.
        """
        raw = self._fetch_from_api()
        parsed = StateVectorsResponse.from_api_response(raw)

        if not parsed.states:
            logger.warning("Empty response from OpenSky API")
            return 0

        records = self._to_records(parsed)
        key = self._build_partition_key()
        self._storage.write_parquet(records, settings.s3_raw_bucket, key)

        logger.info("Ingest complete", records=len(records))
        return len(records)

    def _fetch_from_api(self) -> dict[str, Any]:
        """Fetch raw state vectors from OpenSky API."""
        token = self._token_manager.get_token()
        logger.info("Fetching state vectors from OpenSky")

        try:
            response = httpx.get(
                f"{settings.opensky_api_url}/states/all",
                params={
                    "lamin": settings.bbox_lamin,
                    "lamax": settings.bbox_lamax,
                    "lomin": settings.bbox_lomin,
                    "lomax": settings.bbox_lomax,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0,
            )
        except httpx.RequestError as e:
            raise APIError(0, f"Network error: {e}") from e

        if response.status_code == 429:
            retry_after = int(response.headers.get("X-Rate-Limit-Retry-After-Seconds", 60))
            raise RateLimitError(retry_after)

        if response.status_code != 200:
            raise APIError(response.status_code, response.text)

        return response.json()  # type: ignore[no-any-return]

    def _to_records(self, parsed: StateVectorsResponse) -> list[dict[str, Any]]:
        """Convert parsed Pydantic models to dicts for Parquet serialization."""
        extracted_at = parsed.time
        return [{**sv.model_dump(), "_extracted_at": extracted_at} for sv in parsed.states]

    def _build_partition_key(self) -> str:
        """
        Build S3 key with Hive-style partitioning by date and hour.
        Example: dt=2026-06-21/hour=17/run_20260621T174332.parquet
        """
        now = datetime.now(UTC)
        return (
            f"dt={now.strftime('%Y-%m-%d')}/"
            f"hour={now.strftime('%H')}/"
            f"run_{now.strftime('%Y%m%dT%H%M%S')}.parquet"
        )
