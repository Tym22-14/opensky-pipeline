from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenSky API
    opensky_client_id: str = Field(..., description="OpenSky OAuth2 client ID")
    opensky_client_secret: str = Field(..., description="OpenSky OAuth2 client secret")
    opensky_token_url: str = (
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    )
    opensky_api_url: str = "https://opensky-network.org/api"

    # Bounding box - Europa Centralna
    bbox_lamin: float = 45.0
    bbox_lamax: float = 55.0
    bbox_lomin: float = 10.0
    bbox_lomax: float = 25.0

    # MinIO / S3
    aws_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    s3_raw_bucket: str = "opensky-raw"
    s3_processed_bucket: str = "opensky-processed"

    # BigQuery
    gcp_project_id: str = Field(..., description="Google Cloud project ID")
    bigquery_dataset_raw: str = "opensky_raw"


settings = Settings()  # type: ignore[call-arg]
