class OpenSkyPipelineError(Exception):
    """Base exception for the project. Catch this to handle any pipeline error."""

    pass


class IngestError(OpenSkyPipelineError):
    """Something went wrong fetching data from the OpenSky API or writing to MinIO."""

    pass


class AuthenticationError(IngestError):
    """Failed to authenticate with the API — bad credentials or expired token."""

    pass


class RateLimitError(IngestError):
    """API rate limit hit. retry_after_seconds tells you how long to wait."""

    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Rate limit exceeded. Retry after {retry_after_seconds}s")


class APIError(IngestError):
    """Unexpected status code from the API (e.g. 500, 404)."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"API error {status_code}: {message}")


class StorageError(OpenSkyPipelineError):
    """Read or write failed — MinIO or BigQuery."""

    pass


class ValidationError(OpenSkyPipelineError):
    """Data didn't pass validation — unexpected structure or out-of-range values."""

    pass
