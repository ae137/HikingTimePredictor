import gpxpy

class GpxStats(object):
    def __init__(self, track):
        self.name = track.name if track.name is not None else 'NotAvailable'
        self.length2d = track.length_2d()
        self.length3d = track.length_3d()
        self.duration = float(track.get_duration()) \
            if track.get_duration() is not None else float(-1)
        self.moving_time = track.get_moving_data().moving_time
        self.stopped_time = track.get_moving_data().stopped_time
        self.max_speed = track.get_moving_data().max_speed
        self.total_uphill = track.get_uphill_downhill().uphill
        self.total_downhill = track.get_uphill_downhill().downhill
        
    def toList(self):
        return [self.name, self.length2d, self.length3d, self.duration, \
                self.moving_time, self.stopped_time, self.max_speed, \
                self.total_uphill, self.total_downhill]
    
    def getHeader():
        return ['Name', 'Length2d', 'Length3d', 'Duration', \
                'MovingTime', 'StoppedTime', 'MaxSpeed', \
                'TotalUphill', 'TotalDownhill']
        

def parseGpxFiles(file_name_list):
    gpx_files = []
    for file_name in file_name_list:
        gpx_file = open(file_name, 'r')
        gpx_files.append(gpxpy.parse(gpx_file))
    
    return gpx_files
