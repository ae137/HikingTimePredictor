import collections
from typing import List, Dict, Union
import statistics

from gpxpy import parse                # type: ignore
from gpxpy.gpx import GPXTrackSegment  # type: ignore
import numpy as np                     # type: ignore

from gpx_data_utils import gpx_segment_to_array


class PathFeature:
    "Wrapper class for storing array data in pd.DataFrame."
    def __init__(self, data: np.array):
        self.array_data = data

    @property
    def shape(self):
        return self.array_data.shape

    @property
    def data(self):
        return self.array_data


def convert_path_to_feature(segment: GPXTrackSegment, num_points_path: int) -> np.array:
    """
    Convert GPX track segment to feature.

    :param: segment:         GPX track segment
    :param: num_points_path: Maximal length of track points in path feature

    :return: Rotated and normalized GPX track segment
    """
    def _get_rotation_matrix(phi):
        cos_phi, sin_phi = np.cos(phi), np.sin(phi)
        return np.array([np.array([cos_phi, -sin_phi]),
                         np.array([sin_phi, cos_phi])])

    data = np.zeros((num_points_path, 3))

    assert len(segment.points) > 0, "Path does not contain any points"
    assert len(segment.points) <= num_points_path, "Path too long"

    data[:len(segment.points)] = gpx_segment_to_array(segment)

    # Normalize coordinates
    data[:len(segment.points)] -= data[0]

    # Compute center of gravity of path
    center = np.sum(data, axis=0) / len(segment.points)
    phi = np.arctan2(center[1], center[0])
    m = _get_rotation_matrix(-phi)      # Return points with angle that maps center to x-axis

    for idx in range(len(segment.points)):
        data[idx][0:2] = np.dot(m, data[idx][0:2])

    return data


def convert_paths_to_array(path_features: List[PathFeature]) -> np.array:
    """
    Convert a list of PathFeature objects to an array.

    :param: path_features:  List of PathFeature objects
    :return:                Array of shape (len(path_features), path_features[0].shape)
    """
    return np.array([path_data.data for path_data in path_features])


class GpxSegmentStats(object):
    "Object collecting statistical properties of a GPX segment."

    def __init__(self, segment: GPXTrackSegment, num_points_path: int = 25) -> None:
        """
        Construct GpxSegmentStats object.
        
        :param: segment:         GPX track segment
        :param: num_points_path: Maximal length of points in path features
        """
        self.name = getattr(segment, 'name', 'NotAvailable')
        self.length2d = segment.length_2d()
        self.length3d = segment.length_3d()
        self.duration = float(segment.get_duration()) \
            if segment.get_duration() is not None else float(-1)
        self.moving_time = segment.get_moving_data().moving_time
        self.stopped_time = segment.get_moving_data().stopped_time

        self.total_uphill = segment.get_uphill_downhill().uphill
        self.total_downhill = segment.get_uphill_downhill().downhill

        self.path = convert_path_to_feature(segment, num_points_path)

    def toList(self) -> List[Union[float, PathFeature]]:
        "Convert GpxSegmentStats object data to list."
        entry = [self.length2d, self.length3d, self.duration,
                 self.moving_time, self.stopped_time,
                 self.total_uphill, self.total_downhill, self.path]
        return entry

    def toDict(self) -> Dict[str, Union[float, PathFeature]]:
        "Convert GpxSegmentStats object data to dictionary."
        entry = {'Length2d': self.length2d, 'Length3d': self.length3d,
                 'MovingTime': self.moving_time, 'StoppedTime': self.stopped_time, 'Duration': self.duration,
                 'TotalUphill': self.total_uphill, 'TotalDownhill': self.total_downhill,
                 'Path': self.path}
        return entry

    @classmethod
    def getHeader(cls):
        "Return names of data entries."
        return ['Length2d', 'Length3d', 'Duration',
                'MovingTime', 'StoppedTime',
                'TotalUphill', 'TotalDownhill', 'Path']


def parse_gpx_files(file_name_list: List[str]):
    """
    Parse GPX files and yield their content

    :param: file_name_list:     List of GPX file names
    """
    for file_name in file_name_list:
        with open(file_name, 'r') as gpx_file:
            yield parse(gpx_file)


def get_segments(gpx_file_content_list) -> List[str]:
    gpx_segments_list = []
    for gpx_file_content in gpx_file_content_list:
        for track in gpx_file_content.tracks:
            for segment in track.segments:
                gpx_segments_list.append(segment)

    print("Finished reading", len(gpx_segments_list), "segments.")

    return gpx_segments_list


def parse_gpx_files_return_segments(file_name_list: List[str]) -> List[GPXTrackSegment]:
    """
    Parse GPX files and return list of GPX track segments

    :param: file_name_list: List of GPX files
    :return: List of GPXTrackSegment objects
    """
    gpx_file_contents = parse_gpx_files(file_name_list)
    return get_segments(gpx_file_contents)


def smoothen_coordinates(segments_list: List[GPXTrackSegment], window_size: int = 3) -> None:
    """
    Smoothen coordinates of GPX track segment inplace

    This function smoothens the coordinates in a GPX track, keeping other track information like time stamps
    :param: segments_list:      List of GPX track segments
    :param: window_size:        Size of moving window for averaging
    """
    assert window_size % 2, "Window size should be an odd number, {} given.".format(window_size)
    half_window_size = (window_size - 1) // 2

    for idx in range(len(segments_list)):
        cloned_segment = segments_list[idx].clone()

        if len(segments_list[idx].points) >= window_size:
            for i in range(half_window_size, len(segments_list[idx].points)-half_window_size):
                segments_list[idx].points[i].longitude = \
                    statistics.mean([point.longitude for point in
                                     cloned_segment.points[(i-half_window_size):(i+half_window_size+1)]])
                segments_list[idx].points[i].latitude = \
                    statistics.mean([point.latitude for point in
                                     cloned_segment.points[(i-half_window_size):(i+half_window_size+1)]])

                # Smoothen elevations if all points in the window have elevation information
                elevations = [point.elevation for point in
                              cloned_segment.points[(i-half_window_size):(i+half_window_size+1)]]
                if all(elevations):
                    segments_list[idx].points[i].elevation = \
                        statistics.mean(elevations)

            del segments_list[idx].points[:half_window_size]    # Delete first and last points
            del segments_list[idx].points[-half_window_size:]


def filter_segments(gpx_segments_list: List[GPXTrackSegment], min_distance_m: float = 5) \
        -> List[GPXTrackSegment]:
    """
    Filter points from GPX track segments that are too close to each other

    :param: gpx_segments_list:      List of GPX track segments to be processed
    :param: min_distance_m:         Minimum distance between consecutive track points after filtering

    :return: List of GPX track segments that are all shorter than max_length_m
    """
    gpx_filtered_segments_list = []

    for segment in gpx_segments_list:
        points = [segment.points[0]]
        last_kept = segment.points[0]

        for point in segment.points[1:]:
            if GPXTrackSegment([last_kept, point]).length_2d() > min_distance_m:
                points.append(point)
                last_kept = point

        gpx_filtered_segments_list.append(GPXTrackSegment(points))

    return gpx_filtered_segments_list


def split_segments_by_length(gpx_segments_list: List[GPXTrackSegment], *, max_length_m: int = 100) \
        -> List[GPXTrackSegment]:
    """
    Split GPX track segments until all are shorter than max_length_m

    :param: gpx_segments_list:      List of GPX track segments to be processed
    :param: max_length_m:           Maximum length of track segment above which the segment should be split

    :return: List of GPX track segments that are all shorter than max_length_m
    """
    gpx_split_segments_list = []

    buffer = collections.deque(gpx_segments_list)

    while len(buffer) > 0:
        segment = buffer.popleft()

        if segment.length_2d() < max_length_m:
            gpx_split_segments_list.append(segment)

        else:
            buffer.append(GPXTrackSegment(segment.points[:len(segment.points)//2]))
            buffer.append(GPXTrackSegment(segment.points[len(segment.points)//2:]))

    return gpx_split_segments_list


def filter_bad_segments(gpx_segments_list: List[GPXTrackSegment]) -> List[GPXTrackSegment]:
    """
    Filter segments with obviously insensible data

    This function filters segments with unreasonable data, for example large differences in elevation, arising from
    bad measurements.

    Args:
        gpx_segments_list: List of GPX segments

    Returns:
        Filtered list of GPX segments
    """
    def _elevation_predicate(segment: GPXTrackSegment, max_elevation_diff: int) -> bool:
        uphill, downhill = segment.get_uphill_downhill()

        return (uphill < max_elevation_diff and downhill < max_elevation_diff)

    return list(filter(lambda segment: _elevation_predicate(segment, 500), gpx_segments_list))


def extract_stats(gpx_segments_list: List[GPXTrackSegment], num_points_path: int = 25) -> List[GpxSegmentStats]:
    """
    Extract some properties of GPX track segments

    :param: gpx_segments_list:      List of GPX track segments to be processed
    :param: num_points_path:        Maximum number of points in path features

    :return: List of features extracted from GPX tracks
    """
    gpx_stats = []
    for segment in gpx_segments_list:
        segment_stats = GpxSegmentStats(segment, num_points_path)

        if (segment_stats.moving_time >= segment_stats.stopped_time):
            gpx_stats.append(segment_stats)

    return gpx_stats
