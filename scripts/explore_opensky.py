from opensky_pipeline.ingest.opensky import OpenSkyStateVectorsIngestor
from opensky_pipeline.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    logger.info("Starting end-to-end ingest test")

    ingestor = OpenSkyStateVectorsIngestor()
    count = ingestor.fetch_and_store()

    logger.info("Test complete", records_written=count)


if __name__ == "__main__":
    main()
