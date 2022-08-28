"""Script for formatting GPX data in a format suitable for machine learning."""

import os
import argparse
import glob
from typing import Tuple, List

import h5py

import gpx_stats
from config import DataPreparationConfig, DEFAULT_DATA_PREPARATION_CONFIG
from utils import get_pseudo_probability_for_path


def parse_command_line_arguments() -> Tuple[str, str]:
    """
    Parse command line arguments.

    :return:    Name of base folder and filter key as stings
    """
    description_string = "Prepare data for estimation of walking times from GPX tracks."
    parser = argparse.ArgumentParser(description=description_string)
    parser.add_argument(
        "base_folder", help="Name of base folder to be searched recursively for tracks."
    )
    parser.add_argument(
        "filter_key",
        help="Key for filtering GPX tracks," 'should be in path (for example "Hiking")',
    )
    cmd_line_args = vars(parser.parse_args())

    return cmd_line_args["base_folder"], cmd_line_args["filter_key"]


def get_gpx_file_list(folder: str, key_for_filtering: str) -> List[str]:
    """
    Return list of paths to GPX files in folder.

    :param: folder:                 Folder in which to search for GPX files recursively
    :param: key_for_filtering:      String that should be contained in paths

    :return: List of paths
    """
    return [
        file_path
        for file_path in glob.iglob(os.path.join(folder, "**"), recursive=True)
        if file_path.endswith(".gpx") and key_for_filtering in file_path
    ]


def write_data_to_hdf5(
    gpx_data_list: List[gpx_stats.GpxSegmentStats],
    file_name: str,
    num_points_in_path: int,
) -> None:
    """
    Write GPX dataset to hdf5 file.

    :param: gpx_data_list:           List of objects containing statistical data on GPX track segments
    :param: file_name:               Name of file for storing data
    :param: num_points_path:         Maximum number of points in path feature
    """
    len_gpx_data_list: int = len(gpx_data_list)

    with h5py.File(file_name, "w") as hdf5file:
        dataset_items = {}
        for name in gpx_stats.GpxSegmentStats.get_header():
            shape = (
                (len_gpx_data_list, num_points_in_path, 3)
                if "Path" in name
                else (len_gpx_data_list,)
            )
            dataset_items[name] = hdf5file.create_dataset(name, shape, dtype=float)

        for i in range(len_gpx_data_list):
            stats = gpx_data_list[i].to_dict()
            for name in stats.keys():
                dataset_items[name][i] = stats[name]


def extract_segment_data(
    file_list: List[str], data_preparation_config: DataPreparationConfig
) -> List[gpx_stats.GpxSegmentStats]:
    # Parse gpx files and return track segments for training set
    gpx_segments_list = gpx_stats.parse_gpx_files_return_segments(file_list)
    gpx_stats.smoothen_coordinates(gpx_segments_list)

    gpx_segments_filtered_list = gpx_stats.filter_segments(
        gpx_segments_list, min_distance_m=data_preparation_config.min_distance_m
    )
    gpx_split_segments_list = gpx_stats.split_segments_by_length(
        gpx_segments_filtered_list, max_length_m=data_preparation_config.max_length_m
    )

    if data_preparation_config.filter_bad_segments:
        gpx_split_segments_list = gpx_stats.filter_bad_segments(
            gpx_split_segments_list, data_preparation_config
        )

    # Get track statistics
    return gpx_stats.extract_stats(
        gpx_split_segments_list,
        num_points_path=data_preparation_config.num_points_path,
    )


if __name__ == "__main__":
    base_folder, filter_key = parse_command_line_arguments()
    print("Recursively searching for GPX files in '{}'".format(base_folder))
    print("and filtering files that contain '{}' in their path.".format(filter_key))

    data_prep_config = DEFAULT_DATA_PREPARATION_CONFIG

    # Create list with all gpx files from base_folder that contain filter_key in their path
    file_list_filtered = get_gpx_file_list(base_folder, filter_key)

    # Create train / test split of files
    train_fraction: float = 0.8
    train_file_list = [
        file_name
        for file_name in file_list_filtered
        if get_pseudo_probability_for_path(file_name) < train_fraction
    ]
    test_file_list = [
        file_name
        for file_name in file_list_filtered
        if get_pseudo_probability_for_path(file_name) >= train_fraction
    ]

    # Make sure there is no overlap between the dataset splits
    assert not set(train_file_list).intersection(test_file_list)

    with open("train_file_list.txt", "w") as train_files_output:
        train_files_output.writelines([name + "\n" for name in train_file_list])

    with open("test_file_list.txt", "w") as test_files_output:
        test_files_output.writelines([name + "\n" for name in test_file_list])

    # Parse gpx files and return track segments for training set
    gpx_data_train = extract_segment_data(train_file_list, data_prep_config)

    write_data_to_hdf5(
        gpx_data_train,
        "hiking_data_training.hdf5",
        data_prep_config.num_points_path,
    )

    # Parse gpx files and return track segments for test set
    gpx_data_test = extract_segment_data(test_file_list, data_prep_config)

    write_data_to_hdf5(
        gpx_data_test,
        "hiking_data_test.hdf5",
        data_prep_config.num_points_path,
    )

    print("Finished writing statistics about tracks to hdf5 file.")
