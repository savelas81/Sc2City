import enum
from .config import Paths


class MapTypes(enum.Enum):
    ONE_BASE = Paths.ONE_BASE.value
    STANDARD = Paths.STANDARD.value
    PROXY = Paths.PROXY.value
