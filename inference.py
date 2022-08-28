import argparse
from typing import Optional

import numpy as np
import pandas as pd
import tensorflow as tf

import gpx_stats
import utils
from config import data_preparation_config
from prepare_data import extract_segment_data

parser = argparse.ArgumentParser(
    description="Estimate walking time for GPX track of hiking route."
)
parser.add_argument("input_file", help="Name of input file.")
parser.add_argument(
    "model_type", help="Name of model (Should have been trained before with notebook.)"
)
cmd_line_args = vars(parser.parse_args())

input_file = cmd_line_args["input_file"]
print("Estimating walking time for track in '{}'.".format(input_file))

model_type = cmd_line_args["model_type"]
assert model_type in [
    "simple",
    "recurrent",
    "mixed",
], "Undefined model type. Should be simple, recurrent or mixed."
print("Using '{}' model.".format(model_type))

# Parse gpx files and return track segments
gpx_data = extract_segment_data([input_file], filter_bad_segments=False)

non_path_features = {}
path_features = np.zeros(
    shape=(len(gpx_data), data_preparation_config.num_points_path, 3), dtype=float
)
for name in gpx_stats.GpxSegmentStats.get_header():
    if "Path" not in name:
        non_path_features[name] = np.zeros(shape=(len(gpx_data),), dtype=float)

for i in range(len(gpx_data)):
    stats = gpx_data[i].to_dict()
    for name in stats.keys():
        if "Path" in name:
            path_features[i] = stats[name]
        else:
            non_path_features[name][i] = stats[name]

non_path_features_df = pd.DataFrame.from_dict(non_path_features)

train_stats = pd.read_csv("train_dataset_stats.csv", header=0, sep=" ", index_col=0)

durations = non_path_features_df.pop("Duration")
stopped_time = non_path_features_df.pop("StoppedTime")
moving_time = non_path_features_df.pop("MovingTime")
ground_truth_times = pd.concat([moving_time, stopped_time, durations], axis=1)

# Normalize data for inference:
normalized_non_path_features = (
    (non_path_features_df - train_stats["mean"]) / train_stats["std"]
).values

# TODO: Find better fix for points with missing elevation information in paths at the start of tracks
path_features[np.isnan(path_features)] = 0.0

normalized_non_path_features = normalized_non_path_features.astype(np.float32)
path_features = path_features.astype(np.float32)

# Load model and predict hiking time
if model_type == "simple":
    imported_model = tf.saved_model.load("model_hikingTimePrediction_simple")
    predictions = imported_model(normalized_non_path_features)
elif model_type == "recurrent":
    imported_model = tf.saved_model.load("model_hikingTimePrediction_recurrent")
    predictions = imported_model(path_features)
elif model_type == "mixed":
    imported_model = tf.saved_model.load("model_hikingTimePrediction_mixed")
    predictions = imported_model([normalized_non_path_features, path_features])
else:
    raise ValueError(f"Encountered bad model type {model_type}.")

# Compute standard estimate for comparison
gpx_track = list(gpx_stats.parse_gpx_files([input_file]))[0].tracks[0]  # Complete track
track_length = gpx_track.length_2d()
track_uphill, track_downhill = gpx_track.get_uphill_downhill()
standard_estimate_hiking_time = utils.compute_standard_walking_time(
    track_length, track_uphill, track_downhill
)
true_moving_time: Optional[float] = None
try:
    true_moving_time = gpx_track.get_moving_data().moving_time
    if true_moving_time is not None and true_moving_time > 0:
        print(
            f"The actual moving time based on timestamps was {round(true_moving_time / 3600, 2)} h."
        )

except Exception as e:
    print("Track does not contain timestamps.", e)

print(
    "The predicted moving time for the hike is",
    round(np.sum(predictions[:, 0]) / 3600, 2),
    "h.",
)
print(
    "The predicted standard deviation for the hiking time is",
    round(np.sqrt(np.sum(np.exp(predictions[:, 1]))) / 3600, 2),
    "h.",
)
print(
    "The result of the standard estimate is",
    round(standard_estimate_hiking_time / 3600, 2),
    "h.",
)
