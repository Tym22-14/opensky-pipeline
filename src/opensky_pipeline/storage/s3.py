import io
from typing import Any

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from botocore.exceptions import BotoCoreError, ClientError
from opensky_pipeline.config import settings
from opensky_pipeline.exceptions import StorageError
from opensky_pipeline.logging import get_logger

logger = get_logger(__name__)


class S3Storage:
    """Handles read/write operations to MinIO/S3 using Parquet format."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def write_parquet(
        self,
        records: list[dict[str, Any]],
        bucket: str,
        key: str,
    ) -> None:
        """
        Write a list of dicts to S3/MinIO as a Parquet file.
        Key should include full path with partition structure.
        """
        if not records:
            logger.warning("No records to write", bucket=bucket, key=key)
            return

        try:
            table = pa.Table.from_pylist(records)
            buffer = io.BytesIO()
            pq.write_table(table, buffer)
            buffer.seek(0)
            size = buffer.getbuffer().nbytes

            self._client.put_object(
                Bucket=bucket,
                Key=key,
                Body=buffer.getvalue(),
            )
            logger.info(
                "Written to S3",
                bucket=bucket,
                key=key,
                rows=len(records),
                size_bytes=size,  # użyj poprawnego rozmiaru
            )
        except (BotoCoreError, ClientError) as e:
            raise StorageError(f"Failed to write to s3://{bucket}/{key}: {e}") from e
