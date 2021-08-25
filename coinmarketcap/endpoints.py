from enum import Enum


class CMCEndpoints(Enum):
    v1 = "v1/"
    cryptocurrency = "cryptocurrency/"

    # Cryptocurrency
    map = f"{v1}{cryptocurrency}map"
    info = f"{v1}{cryptocurrency}info"
    listings_latest = f"{v1}{cryptocurrency}listings/latest"
    listings_historical = f"{v1}{cryptocurrency}listings/historical"
    quotes_latest = f"{v1}{cryptocurrency}quotes/latest"
    quotes_historical = f"{v1}{cryptocurrency}v/historical"
