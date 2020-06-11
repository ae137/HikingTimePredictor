import gpxpy
import math
import collections



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
        entry = [self.name, self.length2d, self.length3d, self.duration, \
                 self.moving_time, self.stopped_time, \
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
        gpx_file = open(file_name, 'r')
        gpx_files.append(gpxpy.parse(gpx_file))

    return gpx_files

def split_segments_points(gpx_segments_list):
    gpx_split_segments_list = []
    for segment in gpx_segments_list:
        length_km = segment.length_2d() / 1000
        num_low = math.floor(length_km)
        num_high = math.ceil(length_km)

        len_points_low = len(segment.points) // num_low
        len_points_high = len(segment.points) // num_high

        for i in range(num_low):
            part = gpxpy.gpx.GPXTrackSegment(segment.points[i * len_points_low:
                                                                (i+1) * len_points_low])
            gpx_split_segments_list.append(part)

        for i in range(num_high):
            part = gpxpy.gpx.GPXTrackSegment(segment.points[i * len_points_high:
                                                                (i+1) * len_points_high])
            gpx_split_segments_list.append(part)

    return gpx_split_segments_list

def split_segments(gpx_segments_list):
    gpx_split_segments_list = []

    max_length_m = 100 # 1000
    buffer = collections.deque(gpx_segments_list)

    while len(buffer) > 0:
        segment = buffer.popleft()
        if segment.length_2d() < max_length_m:
            gpx_split_segments_list.append(segment)
        else:
            buffer.append(gpxpy.gpx.GPXTrackSegment(
                segment.points[0:len(segment.points)//2]))
            buffer.append(gpxpy.gpx.GPXTrackSegment(
                segment.points[len(segment.points)//2:]))

    return gpx_split_segments_list
