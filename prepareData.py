import os
import argparse
import glob
import copy
import random
from typing import Tuple, List

import h5py   # type: ignore
import gpxpy  # type: ignore

import gpx_stats


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


def get_gpx_file_list(base_folder: str, filter_key: str) -> List[str]:
    """
    Return list of paths to GPX files in base_folder.

    :param: base_folder:    Folder in which to search for GPX files recursively
    :param: filter_key:     String that should be contained in paths

    :return: List of paths
    """
    return [file_path for file_path in glob.iglob(os.path.join(base_folder, '**'), recursive=True)
            if file_path.endswith('.gpx') and filter_key in file_path]


def write_data_to_hdf5(gpx_data: List[gpx_stats.GpxSegmentStats], file_name: str, num_points_path: int) -> None:
    """
    Write GPX dataset to hdf5 file.

    :param: gpx_data:           List of objects containing statistical data on GPX track segments
    :param: file_name:          Name of file for storing data
    :param: num_points_path:    Maximum number of points in path feature
    """
    with h5py.File(file_name, "w") as hdf5file:
        dataset_items = {}
        for name in gpx_stats.GpxSegmentStats.getHeader():
            shape = (len(gpx_data), num_points_path, 3) if 'Path' in name else (len(gpx_data),)
            dataset_items[name] = hdf5file.create_dataset(name, shape, dtype=float)

        for i in range(len(gpx_data)):
            stats = gpx_data[i].toDict()
            for name in stats.keys():
                dataset_items[name][i] = stats[name]


num_points_path = 25
min_distance_m = 4
max_length_m = 100

base_folder, filter_key = parse_command_line_arguments()
print('Recursively searching for GPX files in \'{}\''.format(base_folder))
print('and filtering files that contain \'{}\' in their path.'.format(filter_key))

# Create list with all gpx files from base_folder that contain filter_key in their path
file_list_filtered = get_gpx_file_list(base_folder, filter_key)

# Parse gpx files and return track segments
gpx_segments_list = gpx_stats.parse_gpx_files_return_segments(file_list_filtered)
gpx_stats.smoothen_coordinates(gpx_segments_list)

gpx_segments_filtered_list = gpx_stats.filter_segments(gpx_segments_list, min_distance_m=min_distance_m)
gpx_split_segments_list = gpx_stats.split_segments_by_length(gpx_segments_filtered_list, max_length_m=max_length_m)

# Get track statistics
gpx_data = gpx_stats.extract_stats(gpx_split_segments_list, num_points_path=num_points_path)

random.shuffle(gpx_data)

max_idx_training_set = int(0.8 * len(gpx_data))

write_data_to_hdf5(gpx_data[:max_idx_training_set], 'hiking_data_training.hdf5', num_points_path)
write_data_to_hdf5(gpx_data[max_idx_training_set:], 'hiking_data_test.hdf5', num_points_path)

print("Finished writing statistics about tracks to hdf5 file.")
