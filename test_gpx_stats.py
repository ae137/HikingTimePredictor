import unittest

import numpy as np
import pandas as pd

from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment

from gpx_data_utils import (
    gpx_point_to_array,
    gpx_segment_to_array,
    gpx_segment_from_array,
)
from gpx_stats import convert_path_to_feature, smoothen_coordinates


class TestConvertPathToArray(unittest.TestCase):
    def setUp(self):
        self.segment_1 = GPXTrackSegment(
            [
                GPXTrackPoint(longitude=0.1, latitude=1, elevation=10),
                GPXTrackPoint(longitude=0.2, latitude=2, elevation=20),
                GPXTrackPoint(longitude=0.3, latitude=3, elevation=30),
            ]
        )
        self.expected_path_1 = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0049875621, 0.0, 10],
                [2.00997512422, 0.0, 20],
                [0.0, 0.0, 0.0],
            ]
        )

    def test_segment_empty(self):
        with self.assertRaises(AssertionError):
            convert_path_to_feature(GPXTrackSegment(), 1)

    def test_segment_too_long(self):
        with self.assertRaises(AssertionError):
            convert_path_to_feature(self.segment_1, 1)

    def test_segment_short(self):
        path = convert_path_to_feature(self.segment_1, 4)
        np.testing.assert_array_almost_equal(path, self.expected_path_1)


class TestSmoothenCoordinatesShort(unittest.TestCase):
    def setUp(self):
        self.segment_1 = GPXTrackSegment(
            [
                GPXTrackPoint(longitude=0.1, latitude=1, elevation=10),
                GPXTrackPoint(longitude=0.2, latitude=2, elevation=20),
                GPXTrackPoint(longitude=0.3, latitude=3, elevation=30),
                GPXTrackPoint(longitude=0.5, latitude=-1, elevation=0),
            ]
        )

        self.expected_1 = GPXTrackSegment(
            [
                GPXTrackPoint(longitude=0.2, latitude=2, elevation=20),
                GPXTrackPoint(longitude=1.0 / 3, latitude=4.0 / 3, elevation=50.0 / 3),
            ]
        )

    def test_segment_list_empty(self):
        smoothen_coordinates([])

    def test_segment_empty(self):
        smoothen_coordinates([GPXTrackSegment()])

    def test_segment_short_1(self):
        input = [GPXTrackSegment(self.segment_1.points[0:3])]
        smoothen_coordinates(input)

        expected_result = [GPXTrackSegment([self.expected_1.points[0]])]

        self.assertEqual(len(input), 1)
        self.assertEqual(len(input[0].points), 1)
        np.testing.assert_array_almost_equal(
            gpx_point_to_array(input[0].points[0]),
            gpx_point_to_array(expected_result[0].points[0]),
        )

    def test_segment_short_2(self):
        input = [GPXTrackSegment(self.segment_1.points)]
        smoothen_coordinates(input)

        expected_result = [self.expected_1]

        self.assertEqual(len(input), 1)
        self.assertEqual(len(input[0].points), len(expected_result[0].points))
        np.testing.assert_array_almost_equal(
            gpx_point_to_array(input[0].points[0]),
            gpx_point_to_array(expected_result[0].points[0]),
        )


class TestSmoothenCoordinatesLonger(unittest.TestCase):
    def setUp(self):
        segment_1_as_array = np.random.normal(scale=5, size=(25, 3))
        segment_1 = gpx_segment_from_array(segment_1_as_array)

        segment_2_as_array = np.random.normal(scale=2, size=(9, 3))
        segment_2 = gpx_segment_from_array(segment_2_as_array)

        self.segments = [segment_1, segment_2]
        self.segments_as_arrays = [segment_1_as_array, segment_2_as_array]

    def test_window_size_3(self):
        expected_as_df = [
            pd.DataFrame(self.segments_as_arrays[i]).rolling(3).mean()[2:]
            for i in range(len(self.segments_as_arrays))
        ]

        smoothen_coordinates(self.segments, window_size=3)

        for i in range(len(self.segments)):
            np.testing.assert_array_almost_equal(
                expected_as_df[i].values, gpx_segment_to_array(self.segments[i])
            )

    def test_window_size_5(self):
        expected_as_df = [
            pd.DataFrame(self.segments_as_arrays[i]).rolling(5).mean()[4:]
            for i in range(len(self.segments_as_arrays))
        ]

        smoothen_coordinates(self.segments, window_size=5)

        for i in range(len(self.segments)):
            np.testing.assert_array_almost_equal(
                expected_as_df[i].values, gpx_segment_to_array(self.segments[i])
            )


if __name__ == "__main__":
    unittest.main()
