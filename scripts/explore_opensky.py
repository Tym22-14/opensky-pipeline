import httpx
from opensky_pipeline.config import settings
from opensky_pipeline.ingest.auth import TokenManager
from opensky_pipeline.ingest.models import StateVectorsResponse
from opensky_pipeline.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()

    tm = TokenManager()
    token = tm.get_token()

    logger.info("Fetching state vectors")
    response = httpx.get(
        f"{settings.opensky_api_url}/states/all",
        params={
            "lamin": settings.bbox_lamin,
            "lamax": settings.bbox_lamax,
            "lomin": settings.bbox_lomin,
            "lomax": settings.bbox_lomax,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()

    # Parsujemy przez model - zamiast state[0], state[5] mamy nazwane pola
    parsed = StateVectorsResponse.from_api_response(response.json())
    logger.info("Parsed response", total_aircraft=len(parsed.states))

    # Pierwsze 3 samoloty - teraz z nazwanymi polami
    for sv in parsed.states[:3]:
        logger.info(
            "Aircraft",
            icao24=sv.icao24,
            callsign=sv.callsign,
            country=sv.origin_country,
            longitude=sv.longitude,
            latitude=sv.latitude,
            altitude=sv.baro_altitude,
            on_ground=sv.on_ground,
        )

    # Pokaz tylko samoloty w powietrzu z wysokością
    airborne = [sv for sv in parsed.states if not sv.on_ground and sv.baro_altitude is not None]
    logger.info(
        "Airborne aircraft stats",
        count=len(airborne),
        avg_altitude=round(
            sum(sv.baro_altitude for sv in airborne if sv.baro_altitude is not None)
            / len(airborne),
            1,
        )
        if airborne
        else 0,
    )


if __name__ == "__main__":
    main()
