import httpx
from opensky_pipeline.config import settings
from opensky_pipeline.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    logger.info("Starting OpenSky exploration")

    # step 1 - get token
    logger.info("Fetching token")
    response = httpx.post(
        settings.opensky_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.opensky_client_id,
            "client_secret": settings.opensky_client_secret,
        },
    )

    token_data = response.json()
    token = token_data["access_token"]
    logger.info("Token fetched", expires_in=token_data["expires_in"])

    # step 2 - fetch aircraft
    logger.info(
        "Fetching state vectors",
        bbox={
            "lamin": settings.bbox_lamin,
            "lamax": settings.bbox_lamax,
        },
    )
    states_response = httpx.get(
        f"{settings.opensky_api_url}/states/all",
        params={
            "lamin": settings.bbox_lamin,
            "lamax": settings.bbox_lamax,
            "lomin": settings.bbox_lomin,
            "lomax": settings.bbox_lomax,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    data = states_response.json()
    states = data.get("states", [])
    logger.info("State vectors fetched", count=len(states))

    # show first 3
    for state in states[:3]:
        logger.info(
            "Sample aircraft",
            icao24=state[0],
            callsign=state[1],
            country=state[2],
            longitude=state[5],
            latitude=state[6],
            altitude=state[7],
            on_ground=state[8],
        )


if __name__ == "__main__":
    main()
