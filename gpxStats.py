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
