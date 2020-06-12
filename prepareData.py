import os
import csv
import argparse
import glob
from typing import Tuple

import gpxpy

import gpxStats


def parse_command_line_arguments() -> Tuple[str, str]:
    """
    Parse command line arguments.

    :return:    Name of base folder and filter key as stings
    """
    description_string = 'Prepare data for estimation of walking times from GPX tracks.'
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument('base_folder',
                        help='Name of base folder to be searched recursively for tracks.')
    parser.add_argument('filter_key', help='Key for filtering GPX tracks,'
                        'should be in path (for example \"Hiking\")')
    cmd_line_args = vars(parser.parse_args())

    return cmd_line_args['base_folder'], cmd_line_args['filter_key']


base_folder, filter_key = parse_command_line_arguments()
print('Recursively searching for GPX files in \'{}\''.format(base_folder))
print('and filtering files that contain \'{}\' in their path.'.format(filter_key))

# Create list with all gpx files from base_folder that contain filter_key in their path
file_list_filtered = [file_path for file_path in glob.iglob(os.path.join(base_folder, '**'), recursive=True) 
                      if file_path.endswith('.gpx') and filter_key in file_path]

# Parse gpx files
gpx_file_list = gpxStats.parseGpxFiles(file_list_filtered)

# Generate list of tracks in files
gpx_segments_list = []
for gpx_file in gpx_file_list:
    for track in gpx_file.tracks:
        for segment in track.segments:
            gpx_segments_list.append(segment)

print("Finished reading", len(gpx_segments_list), "segments.")

# gpx_segments_filtered_list = gpxStats.filter_segments(gpx_segments_list)

gpx_split_segments_list = gpxStats.split_segments(gpx_segments_filtered_list)

# Get track statistics
gpx_stats = []
for segment in gpx_split_segments_list:
    seg_stats = gpxStats.GpxStats(segment)
    if (seg_stats.moving_time > seg_stats.stopped_time):
        gpx_stats.append(seg_stats)

with open('hiking_data.csv', 'w') as csvfile:
    datawriter = csv.writer(csvfile, delimiter=' ')
    datawriter.writerow(gpxStats.GpxStats.getHeader())
    datawriter.writerows([seg_stats.toList() for seg_stats in gpx_stats])

print("Finished writing statistics about tracks to csv file.")

# Insights from analyzing data:
# - Max speed does not contain useful information for estimating times
# - There are a few segments with much higher stopping time than moving time, which
#   presumably result from breaks. These are not very useful for estimating the hiking
#   times as the stopped time can be an order of magnitude larger than the moving time.
#   Thus, we exclude such cases above
#move_list = []
#stop_list = []
#for segment in gpx_split_segments_list:
    #move_list.append(segment.get_moving_data().moving_time)
    #stop_list.append(segment.get_moving_data().stopped_time)
#diff_time_list = [(move - stop) for move, stop in zip(move_list, stop_list)]
#import matplotlib.pyplot as plt
#plt.hist(diff_time_list, 250)
