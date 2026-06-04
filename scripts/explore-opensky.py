import httpx
from opensky_pipeline.config import settings


def main() -> None:
    # Krok 1 - pobierz token
    print("Pobieram token...")
    response = httpx.post(
        settings.opensky_token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.opensky_client_id,
            "client_secret": settings.opensky_client_secret,
        },
    )
    print(f"Status: {response.status_code}")

    token_data = response.json()
    token = token_data["access_token"]
    print(f"Token (pierwsze 30 znaków): {token[:30]}...")
    print(f"Wygasa za: {token_data['expires_in']} sekund")

    # Krok 2 - zapytaj o samoloty nad Europą Centralną
    print("\nPobieram samoloty...")
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
    print(f"Status: {states_response.status_code}")

    data = states_response.json()
    states = data.get("states", [])
    print(f"Liczba samolotów: {len(states)}")

    # Pokaż pierwsze 3 rekordy
    print("\nPierwsze 3 samoloty:")
    for state in states[:3]:
        print(
            f"  ICAO24: {state[0]}, Callsign: {state[1]}, "
            f"Kraj: {state[2]}, Lon: {state[5]}, Lat: {state[6]}, "
            f"Wysokość: {state[7]}m, Na ziemi: {state[8]}"
        )


if __name__ == "__main__":
    main()
