#@title MIT License
#
# Copyright (c) 2019 Andreas Eberlein
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import gpxStats
import gpxpy

import pathlib
import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import gpxStats
import utils

parser = argparse.ArgumentParser(description='Estimate walking time for GPX track of hiking route.')
parser.add_argument('input_file', help='Name of input file.')
cmd_line_args = vars(parser.parse_args())

input_file = cmd_line_args['input_file']
print('Estimating walking time for track described by \"' + input_file + '\".')

gpx_files_parsed = gpxStats.parseGpxFiles([input_file])

gpx_tracks_list = []
for gpx_file in gpx_files_parsed:
    for gpx_track in gpx_file.tracks:
        gpx_tracks_list.append(gpx_track)
        
gpx_tracks_stats = []
for track in gpx_tracks_list:
    gpx_tracks_stats.append(gpxStats.GpxStats(track))

# Format data in such a way that we can process it as in the training step
# Note: This can easily be extended for a list of input tracks. Then the dictionary should just
#    have lists of values instead of one value
raw_input_data = {}
for key, value in zip(gpxStats.GpxStats.getHeader(), gpx_tracks_stats[0].toList()):
    raw_input_data[key] = [value]
    
inference_data = pd.DataFrame(data=raw_input_data)

# Drop unnecessary columns
inference_data.pop('Name')
inference_data.pop('Duration')
inference_data.pop('StoppedTime')
inference_data.pop('MaxSpeed')
inference_data.pop('MovingTime')

# Load data for mean and std for normalization of input data
train_stats = pd.read_csv('train_stats.csv', header=0, sep=' ')

# Normalize data for inference:
normed_inference_data = (inference_data.values - train_stats['mean'].values) \
    / train_stats['std'].values 

# Load the model and compute hiking time
imported_model = keras.models.load_model('model_hikingTimePrediction.h5')
predicted_hiking_times_s = imported_model.predict(normed_inference_data)[0]

# Compute standard estimate for comparison
standard_estimate_hiking_time = utils.compute_standard_walking_time(gpx_tracks_stats[0].length2d,
                                                        gpx_tracks_stats[0].total_uphill,
                                                        gpx_tracks_stats[0].total_downhill)

print('The predicted moving time for the hike is',
      round(predicted_hiking_times_s[0] / 3600, 2), 'h.')
print('The predicted stopping time for the hike is',
      round(predicted_hiking_times_s[1] / 3600, 2), 'h.')
print('The predicted total duration of the hike is',
      round(predicted_hiking_times_s[2] / 3600, 2), 'h.')
print('The result of the standard estimate is',
        round(standard_estimate_hiking_time / 3600, 2), 'h.')

