from typing import Any

from pydantic import BaseModel, Field, field_validator


class StateVector(BaseModel):
    """
    Single aircraft position snapshot from OpenSky /states/all endpoint.
    OpenSky returns each state as an array - we map by position index.
    """

    icao24: str
    callsign: str | None = None
    origin_country: str
    time_position: int | None = None
    last_contact: int
    longitude: float | None = None
    latitude: float | None = None
    baro_altitude: float | None = None
    on_ground: bool
    velocity: float | None = None
    true_track: float | None = None
    vertical_rate: float | None = None
    geo_altitude: float | None = None
    squawk: str | None = None
    spi: bool = False
    position_source: int = 0

    @field_validator("callsign", mode="before")
    @classmethod
    def strip_callsign(cls, v: str | None) -> str | None:
        """OpenSky pads callsigns with spaces - strip them."""
        return v.strip() if v else None

    @classmethod
    def from_array(cls, array: list[Any]) -> "StateVector":
        """
        Parse a state vector from OpenSky's positional array format.
        Index mapping: https://openskynetwork.github.io/opensky-api/rest.html
        """
        return cls(
            icao24=array[0],
            callsign=array[1],
            origin_country=array[2],
            time_position=array[3],
            last_contact=array[4],
            longitude=array[5],
            latitude=array[6],
            baro_altitude=array[7],
            on_ground=array[8],
            velocity=array[9],
            true_track=array[10],
            vertical_rate=array[11],
            geo_altitude=array[13],
            squawk=array[14],
            spi=array[15],
            position_source=array[16],
        )


class StateVectorsResponse(BaseModel):
    """Full response from OpenSky /states/all endpoint."""

    time: int
    states: list[StateVector] = Field(default_factory=list)

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "StateVectorsResponse":
        """Parse raw API response dict into typed model."""
        raw_states = data.get("states") or []
        return cls(
            time=data["time"],
            states=[StateVector.from_array(s) for s in raw_states],
        )
