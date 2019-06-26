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

def compute_standard_walking_time(length_m, elevation_gain_m, elevation_loss_m):
    """Estimate the hiking time in seconds
    
    Parameters
    ----------
    length_m: float
            Length of the hike in meters
    elevation_gain_m: float
            Elevation gain of the hike in meters
    elevation_loss_m: float
            Elevation loss of the hike in meters
    
    Returns
    -------
    walking_time: float
            Walking time (= moving time) for the hike in seconds
    """
    walking_time_length_s = 0.9 * length_m          # assumed speed: 4 km/h
    walking_time_up_s = elevation_gain_m * 12       # assumed speed: +300 m/h
    walking_time_down_s = elevation_loss_m * 7.2    # assumed speed: -500 m/h
    walking_time_up_down_s = walking_time_up_s + walking_time_down_s
    return max(walking_time_length_s, walking_time_up_down_s) + \
        0.5 * min(walking_time_length_s, walking_time_up_down_s)
