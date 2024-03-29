from typing import Final

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DataPreparationConfig:
    num_points_path: int
    min_distance_m: float
    max_length_m: float
    max_elevation_diff_m: float
    filter_bad_segments: bool


DEFAULT_DATA_PREPARATION_CONFIG: Final[DataPreparationConfig] = DataPreparationConfig(
    num_points_path=25,
    min_distance_m=4.0,
    max_length_m=100.0,
    max_elevation_diff_m=100.0,
    filter_bad_segments=True,
)
