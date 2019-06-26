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

import os

def getFileList(folder_name):
    """Get list of paths to gpx files in folder including subfolders
    
    Parameters
    ----------
    folder_name: string
            Name of folder in which to search for gpx files recursively
    
    Returns
    -------
    file_list: list
            List of paths to gpx files
    """
    file_list = []
    folder_content = os.listdir(folder_name)
    for entry in folder_content:
        path_to_file = os.path.join(folder_name, entry)
        if os.path.isfile(path_to_file):
            if path_to_file[-4:] == '.gpx':
                file_list.append(path_to_file)
        else:
            file_list.extend(getFileList(os.path.join(folder_name, entry)))
    return file_list
