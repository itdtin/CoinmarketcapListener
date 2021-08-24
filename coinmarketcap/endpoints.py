from enum import Enum


class CMCEndpoints(Enum):
    v1 = "v1/"
    cryptocurrency = "cryptocurrency/"

    # Cryptocurrency
    map = f"{v1}{cryptocurrency}map"
