import pandas as pd
import s3fs
from opensky_pipeline.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    configure_logging()

    fs = s3fs.S3FileSystem(
        endpoint_url="http://localhost:9000",
        key="minioadmin",
        secret="minioadmin",
    )

    files = fs.glob("opensky-raw/dt=*/**/*.parquet")
    logger.info("Files found in MinIO", count=len(files), files=files)

    if not files:
        logger.warning("No files found - run explore_opensky.py first")
        return

    df = pd.read_parquet(files[0], filesystem=fs)
    logger.info("File loaded", shape=df.shape, columns=list(df.columns))

    print("\nFirst 5 rows:")
    print(df[["icao24", "callsign", "latitude", "longitude", "baro_altitude"]].head())

    print("\nBasic stats:")
    print(f"Total records: {len(df)}")
    print(f"Airborne: {(~df['on_ground']).sum()}")
    print(f"On ground: {df['on_ground'].sum()}")
    print(f"Avg altitude: {df['baro_altitude'].mean():.0f}m")


if __name__ == "__main__":
    main()
