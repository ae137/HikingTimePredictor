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

import gpxpy
import csv
import argparse

import gpxStats
import read_directory_recursively

description_string='Prepare data for estimation of walking time for hiking route described by GPX track.'
parser = argparse.ArgumentParser(description=description_string)
parser.add_argument('base_folder', help='Name of base folder to be searched recursively for tracks.')
parser.add_argument('filter_key', help='Key for filtering GPX tracks, should be in path (for example \"Hiking\")')
cmd_line_args = vars(parser.parse_args())

base_folder = cmd_line_args['base_folder']
filter_key = cmd_line_args['filter_key']
print('Recursively searching for GPX files in \"' + base_folder + '\".')
print('and filtering files that contain \"' + filter_key + '\" in their path.')

file_list = read_directory_recursively.getFileList(base_folder)

# Create list with all files that contain Wandern (=Hiking) in their path
file_list_filtered = [file_path for file_path in file_list if filter_key in file_path]

# Parse gpx files
gpx_file_list = gpxStats.parseGpxFiles(file_list_filtered)

# Generate list of tracks in files
gpx_tracks_list = []
for gpx_file in gpx_file_list:
    for gpx_track in gpx_file.tracks:
        gpx_tracks_list.append(gpx_track)
        
print("Finished reading", len(gpx_tracks_list), " tracks.")

# Get track statistics
gpx_tracks_stats = []
for track in gpx_tracks_list:
    gpx_tracks_stats.append(gpxStats.GpxStats(track))
    
with open('hiking_data.csv', 'w') as csvfile:
    datawriter = csv.writer(csvfile, delimiter=' ')
    datawriter.writerow(gpxStats.GpxStats.getHeader())
    datawriter.writerows([track_stats.toList() for track_stats in gpx_tracks_stats])

print("Finished writing statistics about tracks to csv file.")
