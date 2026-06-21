import httpx
from opensky_pipeline.config import settings
from opensky_pipeline.ingest.auth import TokenManager
from opensky_pipeline.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    logger.info("Starting TokenManager test")

    tm = TokenManager()

    logger.info("Getting token - first call")
    token1 = tm.get_token()
    logger.info("Got token", preview=token1[:20])

    logger.info("Getting token - second call")
    token2 = tm.get_token()

    logger.info("Tokens identical", result=token1 == token2)

    logger.info("Fetching state vectors")
    response = httpx.get(
        f"{settings.opensky_api_url}/states/all",
        params={
            "lamin": settings.bbox_lamin,
            "lamax": settings.bbox_lamax,
            "lomin": settings.bbox_lomin,
            "lomax": settings.bbox_lomax,
        },
        headers={"Authorization": f"Bearer {tm.get_token()}"},
    )
    data = response.json()
    states = data.get("states", [])
    logger.info("State vectors fetched", count=len(states))


if __name__ == "__main__":
    main()
