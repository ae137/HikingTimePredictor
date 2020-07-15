from __future__ import absolute_import, division, print_function, unicode_literals

import os
import csv
import gpxpy                        # type: ignore

import pathlib
import argparse

import matplotlib.pyplot as plt     # type: ignore
import numpy as np                  # type: ignore
import pandas as pd                 # type: ignore

import tensorflow as tf             # type: ignore

import gpx_stats
import utils

num_points_path = 25
min_distance_m = 4
max_length_m = 100

parser = argparse.ArgumentParser(description='Estimate walking time for GPX track of hiking route.')
parser.add_argument('input_file', help='Name of input file.')
parser.add_argument('model_type', help='Name of model (Should have been trained before with notebook.)')
cmd_line_args = vars(parser.parse_args())

input_file = cmd_line_args['input_file']
print("Estimating walking time for track in '{}'.".format(input_file))

model_type = cmd_line_args['model_type']
assert model_type in ['simple', 'recurrent', 'mixed'], "Undefined model type. Should be simple, recurrent or mixed."
print("Using '{}' model.".format(model_type))

# Parse gpx files and return track segments
gpx_track = list(gpx_stats.parse_gpx_files([input_file]))[0].tracks[0]  # Complete track
gpx_segments_list = gpx_stats.parse_gpx_files_return_segments([input_file])
gpx_stats.smoothen_coordinates(gpx_segments_list)

gpx_segments_filtered_list = gpx_stats.filter_segments(gpx_segments_list, min_distance_m=min_distance_m)
gpx_split_segments_list = gpx_stats.split_segments_by_length(gpx_segments_filtered_list, max_length_m=max_length_m)

# Get track statistics
gpx_data = gpx_stats.extract_stats(gpx_split_segments_list, num_points_path=num_points_path)

non_path_features = {}
path_features = np.zeros(shape=(len(gpx_data), num_points_path, 3), dtype=np.float)
for name in gpx_stats.GpxSegmentStats.getHeader():
    if 'Path' not in name:
        non_path_features[name] = np.zeros(shape=(len(gpx_data),), dtype=float)

for i in range(len(gpx_data)):
    stats = gpx_data[i].toDict()
    for name in stats.keys():
        if 'Path' in name:
            path_features[i] = stats[name]
        else:
            non_path_features[name][i] = stats[name]

non_path_features_df = pd.DataFrame.from_dict(non_path_features)

train_stats = pd.read_csv('train_dataset_stats.csv', header=0, sep=' ', index_col=0) 

durations = non_path_features_df.pop('Duration')
stopped_time = non_path_features_df.pop('StoppedTime')
moving_time = non_path_features_df.pop('MovingTime')
ground_truth_times = pd.concat([moving_time, stopped_time, durations], axis=1)

# Normalize data for inference:
normalized_non_path_features = ((non_path_features_df - train_stats['mean']) / train_stats['std']).values

# Load model and predict hiking time
if model_type == 'simple':
    imported_model = tf.keras.models.load_model('model_hikingTimePrediction_simple.h5')
    predicted_hiking_times_s = imported_model.predict(normalized_non_path_features)
elif model_type == 'recurrent':
    imported_model = tf.keras.models.load_model('model_hikingTimePrediction_recurrent.h5')
    predicted_hiking_times_s = imported_model.predict(path_features)
else:
    imported_model = tf.keras.models.load_model('model_hikingTimePrediction_mixed.h5')
    predicted_hiking_times_s = imported_model.predict([normalized_non_path_features, path_features])

# Compute standard estimate for comparison
track_length = gpx_track.length_2d()
track_uphill, track_downhill = gpx_track.get_uphill_downhill()
standard_estimate_hiking_time = utils.compute_standard_walking_time(track_length,
                                                                    track_uphill,
                                                                    track_downhill)

print('The predicted moving time for the hike is',
      round(np.sum(predicted_hiking_times_s[:, 0]) / 3600, 2), 'h.')
print('The predicted total duration of the hike is',
      round(np.sum(predicted_hiking_times_s[:, 2]) / 3600, 2), 'h.')
print('The result of the standard estimate is',
      round(standard_estimate_hiking_time / 3600, 2), 'h.')

