import math
import collections
from typing import List

import gpxpy


class GpxStats(object):
    def __init__(self, track):
        # self.name = name if name is not None else 'NotAvailable'
        self.name = getattr(track, 'name', 'NotAvailable')
        self.length2d = track.length_2d()
        self.length3d = track.length_3d()
        self.duration = float(track.get_duration()) \
            if track.get_duration() is not None else float(-1)
        self.moving_time = track.get_moving_data().moving_time
        self.stopped_time = track.get_moving_data().stopped_time

        self.total_uphill = track.get_uphill_downhill().uphill
        self.total_downhill = track.get_uphill_downhill().downhill

    def toList(self):
        entry = [self.name, self.length2d, self.length3d, self.duration,
                 self.moving_time, self.stopped_time,
                 self.total_uphill, self.total_downhill]
        return entry

    @classmethod
    def getHeader(cls):
        return ['Name', 'Length2d', 'Length3d', 'Duration',
                'MovingTime', 'StoppedTime',
                'TotalUphill', 'TotalDownhill']


def parseGpxFiles(file_name_list):
    gpx_files = []
    for file_name in file_name_list:
        with open(file_name, 'r') as gpx_file:
            gpx_files.append(gpxpy.parse(gpx_file))

    return gpx_files


def filter_segments(gpx_segments_list: List[gpxpy.gpx.GPXTrackSegment], min_distance_m: float = 5) \
        -> List[gpxpy.gpx.GPXTrackSegment]:
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
            if gpxpy.gpx.GPXTrackSegment([last_kept, point]).length_2d() > min_distance_m:
                points.append(point)
                last_kept = point

        gpx_filtered_segments_list.append(gpxpy.gpx.GPXTrackSegment(points))

    return gpx_filtered_segments_list


def split_segments(gpx_segments_list: List[gpxpy.gpx.GPXTrackSegment], max_length_m: int = 100) \
        -> List[gpxpy.gpx.GPXTrackSegment]:
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
            buffer.append(gpxpy.gpx.GPXTrackSegment(segment.points[:len(segment.points)//2]))
            buffer.append(gpxpy.gpx.GPXTrackSegment(segment.points[len(segment.points)//2:]))

    return gpx_split_segments_list
