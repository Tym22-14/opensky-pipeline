import threading
import time
from dataclasses import dataclass

import httpx

from opensky_pipeline.config import settings
from opensky_pipeline.exceptions import AuthenticationError
from opensky_pipeline.logging import get_logger

logger = get_logger(__name__)


@dataclass
class _CachedToken:
    value: str
    expires_at: float  # unix timestamp


class TokenManager:
    """Manages OpenSky OAuth2 token with in-memory caching and auto-refresh."""

    _REFRESH_BUFFER_SECONDS = 60

    def __init__(self) -> None:
        self._cached: _CachedToken | None = None
        self._lock = threading.Lock()  # prevents duplicate fetches under concurrent Airflow tasks

    def get_token(self) -> str:
        """Return a valid OAuth2 token, fetching a new one if needed."""
        with self._lock:
            if self._is_valid():
                logger.debug("Returning cached token")
                return self._cached.value  # type: ignore[union-attr]
            return self._fetch_and_cache()

    def _is_valid(self) -> bool:
        if self._cached is None:
            return False
        return self._cached.expires_at - time.time() > self._REFRESH_BUFFER_SECONDS

    def _fetch_and_cache(self) -> str:
        logger.info("Fetching new OpenSky token")
        try:
            response = httpx.post(
                settings.opensky_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.opensky_client_id,
                    "client_secret": settings.opensky_client_secret,
                },
                timeout=10.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(
                f"Failed to fetch token: HTTP {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise AuthenticationError(f"Network error fetching token: {e}") from e

        data = response.json()
        self._cached = _CachedToken(
            value=data["access_token"],
            expires_at=time.time() + data["expires_in"],
        )
        logger.info("Token fetched", expires_in_seconds=data["expires_in"])
        return self._cached.value
