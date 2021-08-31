import unittest

import numpy as np                                    # type: ignore
import pandas as pd                                   # type: ignore
from gpxpy.gpx import GPXTrackPoint, GPXTrackSegment  # type: ignore

from gpx_data_utils import (
    gpx_point_from_array,
    gpx_point_to_array,
    gpx_segment_to_array,
    gpx_segment_from_array,
    gpx_segment_from_data_frame
)


class TestPointConversions(unittest.TestCase):
    def setUp(self):
        self.point_as_array = np.array([1., 2., 3.])

        self.point = GPXTrackPoint(longitude=1., latitude=2., elevation=3.)

        self.attributes_to_test = ['longitude', 'latitude', 'elevation']

    def test_point_to_array(self):
        point_as_array = gpx_point_to_array(self.point)
        np.testing.assert_array_almost_equal(point_as_array, self.point_as_array)

    def test_array_to_point(self):
        point = gpx_point_from_array(self.point_as_array)

        for attribute in self.attributes_to_test:
            self.assertAlmostEqual(getattr(point, attribute), getattr(self.point, attribute))

    def test_roundtrip(self):
        for i in range(25):
            data = np.random.normal(size=(3,))
            point = gpx_point_from_array(data)
            data_from_point = gpx_point_to_array(point)
            np.testing.assert_array_almost_equal(data, data_from_point)


class TestSegmentConversions(unittest.TestCase):
    def setUp(self):
        self.short_segment_as_array = np.array([[1., 0., 3]])
        self.short_segment = GPXTrackSegment([gpx_point_from_array(self.short_segment_as_array[0])])

        self.long_segment_as_array = np.random.normal(size=(25, 3))
        self.long_segment = GPXTrackSegment([gpx_point_from_array(point_data)
                                             for point_data in self.long_segment_as_array])

    def test_segment_to_array_short(self):
        short_segment_as_array = gpx_segment_to_array(self.short_segment)
        self.assertEqual(short_segment_as_array.shape[1], 3)
        np.testing.assert_array_almost_equal(self.short_segment_as_array, short_segment_as_array)

    def test_array_to_segment_short(self):
        short_segment = gpx_segment_from_array(self.short_segment_as_array)

        self.assertEqual(len(short_segment.points), len(self.short_segment.points))

        for i in range(len(short_segment.points)):
            np.testing.assert_array_almost_equal(gpx_point_to_array(short_segment.points[i]),
                                                 gpx_point_to_array(self.short_segment.points[i]))

    def test_segment_to_array_long(self):
        long_segment_as_array = gpx_segment_to_array(self.long_segment)
        self.assertEqual(long_segment_as_array.shape[1], 3)
        np.testing.assert_array_almost_equal(self.long_segment_as_array, long_segment_as_array)

    def test_array_to_segment_long(self):
        long_segment = gpx_segment_from_array(self.long_segment_as_array)

        self.assertEqual(len(long_segment.points), len(self.long_segment.points))

        for i in range(len(long_segment.points)):
            np.testing.assert_array_almost_equal(gpx_point_to_array(long_segment.points[i]),
                                                 gpx_point_to_array(self.long_segment.points[i]))

    def test_bad_input_dim(self):
        with self.assertRaises(AssertionError):
            gpx_segment_from_array(np.random.normal(size=(7, 4)))

        with self.assertRaises(AssertionError):
            gpx_segment_from_array(np.random.normal(size=(7, 2)))


class TestSegmentDataFrameConversions(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'longitude': [1, -1.5, 0.5], 'latitude': [-2, 37, 15],
                                'elevation': [5, 1005, 3]})

    def test_empty(self):
        result = gpx_segment_from_data_frame(pd.DataFrame({'longitude': [], 'latitude': [], 'elevation': []}))
        self.assertEqual(len(result.points), 0)

    def test_simple(self):
        segment_from_df = gpx_segment_from_data_frame(self.df)
        segment_from_array = gpx_segment_from_array(self.df.values)

        self.assertEqual(len(segment_from_df.points), len(segment_from_array.points))

        for i in range(len(segment_from_df.points)):
            np.testing.assert_array_almost_equal(gpx_point_to_array(segment_from_df.points[i]),
                                                 gpx_point_to_array(segment_from_array.points[i]))


if __name__ == '__main__':
    unittest.main()
