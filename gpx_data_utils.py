from typing import Sequence

import numpy as np                                    # type: ignore
import pandas as pd                                   # type: ignore
from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment  # type: ignore


def gpx_point_to_array(point: GPXTrackPoint) -> np.array:
    "Convert a GPX point to an array."
    return np.array([point.longitude, point.latitude, point.elevation])


def gpx_point_from_array(point_data: np.array) -> GPXTrackPoint:
    "Create a GPXTrackPoint from an array."
    return GPXTrackPoint(longitude=point_data[0], latitude=point_data[1], elevation=point_data[2])


def gpx_segment_to_array(segment: GPXTrackSegment) -> np.array:
    """
    Convert data in GPX track segment into an array

    :param: segment: GPX track segment
    :return: Data as array
    """
    return np.array([gpx_point_to_array(point) for point in segment.points])


def gpx_segment_from_array(segment_data: np.array) -> GPXTrackSegment:
    """
    Create GPX track segment from data in array

    :param: segment_data: Track data as array
    :return: GPX track segment
    """
    assert segment_data.shape[1] == 3, "Length of data items does not have the right shape"

    points = [gpx_point_from_array(segment_data[i]) for i in range(segment_data.shape[0])]

    return GPXTrackSegment(points)


def gpx_segment_to_data_frame(segment: GPXTrackSegment) -> pd.DataFrame:
    """
    Create pandas dataframe from GPX track segment

    :param: segment: GPX track segment
    :return: Pandas dataframe
    """
    columns = ['longitude', 'latitude', 'elevation']

    return pd.DataFrame(gpx_segment_to_array(segment), columns=columns)


def gpx_segment_from_data_frame(df: pd.DataFrame) -> GPXTrackSegment:
    """
    Create GPX track segment from data in Pandas DataFrame

    :param: df: Pandas dataframe containing GPX data
    :return: GPX track segment
    """
    columns = ['longitude', 'latitude', 'elevation']

    assert columns == list(df.columns), "Wrong columns or wrong order of columns in dataframe"

    return gpx_segment_from_array(df.values)
