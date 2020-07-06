from typing import Sequence

import numpy as np
import pandas as pd
from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment

def GPXPointToArray(point: GPXTrackPoint) -> Sequence[float]:
    return np.array([point.longitude, point.latitude, point.elevation])

def GPXPointFromArray(point_data: Sequence[float]) -> GPXTrackPoint:
    return GPXTrackPoint(longitude=point_data[0], latitude=point_data[1], elevation=point_data[2])

def GPXSegmentToArray(segment: GPXTrackSegment) -> Sequence[Sequence[float]]:
    """
    Convert data in GPX track segment into an array
    
    :param: segment: GPX track segment
    :return: Data as array
    """
    array_data = []
    
    for point in segment.points:
        array_data.append(GPXPointToArray(point))
        
    return np.array(array_data)

def GPXSegmentFromArray(segment_data: Sequence[Sequence[float]]) -> GPXTrackSegment:
    """
    Create GPX track segment from data in array
    
    :param: segment_data: Track data as array
    :return: GPX track segment
    """
    assert segment_data.shape[1] == 3, "Length of data items does not have the right shape"
    
    points = []
    
    for i in range(segment_data.shape[0]):
        points.append(GPXPointFromArray(segment_data[i]))
    
    return GPXTrackSegment(points)

def GPXSegmentToDataFrame(segment: GPXTrackSegment) -> pd.DataFrame:
    """
    Create pandas dataframe from GPX track segment
    
    :param: segment: GPX track segment
    :return: Pandas dataframe
    """
    columns = ['longitude', 'latitude', 'elevation']
    
    return pd.DataFrame(GPXSegmentToArray(segment), columns=columns)

def GPXSegmentFromDataFrame(df: pd.DataFrame) -> GPXTrackSegment:
    """
    Create GPX track segment from data in Pandas DataFrame
    
    :param: df: Pandas dataframe containing GPX data
    :return: GPX track segment
    """
    columns = ['longitude', 'latitude', 'elevation']
    
    assert columns == list(df.columns), "Wrong columns or wrong order of columns in dataframe"
    
    return GPXSegmentFromArray(df.values)
