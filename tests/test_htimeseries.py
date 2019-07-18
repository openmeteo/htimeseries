import datetime as dt
import textwrap
from io import StringIO
from unittest import TestCase

import numpy as np
import pandas as pd
from iso8601 import parse_date

from htimeseries import HTimeseries

tenmin_test_timeseries = textwrap.dedent(
    """\
    2008-02-07 11:20,1141.00,
    2008-02-07 11:30,1142.01,MISS
    2008-02-07 11:40,1154.02,
    2008-02-07 11:50,,
    2008-02-07 12:00,1180.04,
    """
)

tenmin_test_timeseries_file_version_2 = textwrap.dedent(
    """\
    Version=2\r
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Nominal_offset=0,0\r
    Actual_offset=0,0\r
    Variable=temperature\r
    Precision=1\r
    \r
    2008-02-07 11:20,1141.0,\r
    2008-02-07 11:30,1142.0,MISS\r
    2008-02-07 11:40,1154.0,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.0,\r
    """
)

tenmin_test_timeseries_file_version_3 = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Nominal_offset=0,0\r
    Actual_offset=0,0\r
    Variable=temperature\r
    Precision=1\r
    Location=24.678900 38.123450 4326\r
    Altitude=219.22\r
    \r
    2008-02-07 11:20,1141.0,\r
    2008-02-07 11:30,1142.0,MISS\r
    2008-02-07 11:40,1154.0,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.0,\r
    """
)

tenmin_test_timeseries_file_version_4 = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Precision=1\r
    Location=24.678900 38.123450 4326\r
    Altitude=219.22\r
    \r
    2008-02-07 11:20,1141.0,\r
    2008-02-07 11:30,1142.0,MISS\r
    2008-02-07 11:40,1154.0,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.0,\r
    """
)

tenmin_test_timeseries_file_no_altitude = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Precision=1\r
    Location=24.678900 38.123450 4326\r
    \r
    2008-02-07 11:20,1141.0,\r
    2008-02-07 11:30,1142.0,MISS\r
    2008-02-07 11:40,1154.0,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.0,\r
    """
)

tenmin_test_timeseries_file_no_location = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Precision=1\r
    \r
    2008-02-07 11:20,1141.0,\r
    2008-02-07 11:30,1142.0,MISS\r
    2008-02-07 11:40,1154.0,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.0,\r
    """
)

tenmin_test_timeseries_file_no_precision = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Location=24.678900 38.123450 4326\r
    Altitude=219.22\r
    \r
    2008-02-07 11:20,1141.000000,\r
    2008-02-07 11:30,1142.010000,MISS\r
    2008-02-07 11:40,1154.020000,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180.040000,\r
    """
)

tenmin_test_timeseries_file_zero_precision = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Precision=0\r
    Location=24.678900 38.123450 4326\r
    Altitude=219.22\r
    \r
    2008-02-07 11:20,1141,\r
    2008-02-07 11:30,1142,MISS\r
    2008-02-07 11:40,1154,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180,\r
    """
)


tenmin_test_timeseries_file_negative_precision = textwrap.dedent(
    """\
    Unit=°C\r
    Count=5\r
    Title=A test 10-min time series\r
    Comment=This timeseries is extremely important\r
    Comment=because the comment that describes it\r
    Comment=spans five lines.\r
    Comment=\r
    Comment=These five lines form two paragraphs.\r
    Timezone=EET (UTC+0200)\r
    Time_step=10,0\r
    Timestamp_rounding=0,0\r
    Timestamp_offset=0,0\r
    Variable=temperature\r
    Precision=-1\r
    Location=24.678900 38.123450 4326\r
    Altitude=219.22\r
    \r
    2008-02-07 11:20,1140,\r
    2008-02-07 11:30,1140,MISS\r
    2008-02-07 11:40,1150,\r
    2008-02-07 11:50,,\r
    2008-02-07 12:00,1180,\r
    """
)

standard_empty_dataframe = pd.DataFrame(
    data={"value": np.array([], dtype=np.float64), "flags": np.array([], dtype=str)},
    index=[],
    columns=["value", "flags"],
)
standard_empty_dataframe.index.name = "date"


class HTimeseriesEmptyTestCase(TestCase):
    def test_read_empty(self):
        s = StringIO()
        ts = HTimeseries(s)
        pd.testing.assert_frame_equal(ts.data, standard_empty_dataframe)

    def test_write_empty(self):
        ts = HTimeseries()
        s = StringIO()
        ts.write(s)
        self.assertEqual(s.getvalue(), "")

    def test_create_empty(self):
        pd.testing.assert_frame_equal(HTimeseries().data, standard_empty_dataframe)


class HTimeseriesWriteSimpleTestCase(TestCase):
    def test_write(self):
        anp = np.array(
            [
                [parse_date("2005-08-23 18:53"), 93, ""],
                [parse_date("2005-08-24 19:52"), 108.7, ""],
                [parse_date("2005-08-25 23:59"), 28.3, "HEARTS SPADES"],
                [parse_date("2005-08-26 00:02"), float("NaN"), ""],
                [parse_date("2005-08-27 00:02"), float("NaN"), "DIAMONDS"],
            ]
        )
        data = pd.DataFrame(anp[:, [1, 2]], index=anp[:, 0], columns=("value", "flags"))
        ts = HTimeseries(data=data)
        s = StringIO()
        ts.write(s)
        self.assertEqual(
            s.getvalue(),
            textwrap.dedent(
                """\
                2005-08-23 18:53,93,\r
                2005-08-24 19:52,108.7,\r
                2005-08-25 23:59,28.3,HEARTS SPADES\r
                2005-08-26 00:02,,\r
                2005-08-27 00:02,,DIAMONDS\r
                """
            ),
        )


class HTimeseriesWriteFileTestCase(TestCase):
    def setUp(self):
        data = pd.read_csv(
            StringIO(tenmin_test_timeseries),
            parse_dates=[0],
            usecols=["date", "value", "flags"],
            index_col=0,
            header=None,
            names=("date", "value", "flags"),
            dtype={"value": np.float64, "flags": str},
        ).asfreq("10T")
        self.reference_ts = HTimeseries(data=data)
        self.reference_ts.timestamp_rounding = "0,0"
        self.reference_ts.timestamp_offset = "0,0"
        self.reference_ts.unit = "°C"
        self.reference_ts.title = "A test 10-min time series"
        self.reference_ts.precision = 1
        self.reference_ts.time_step = "10,0"
        self.reference_ts.timezone = "EET (UTC+0200)"
        self.reference_ts.variable = "temperature"
        self.reference_ts.comment = (
            "This timeseries is extremely important\n"
            "because the comment that describes it\n"
            "spans five lines.\n\n"
            "These five lines form two paragraphs."
        )
        self.reference_ts.location = {
            "abscissa": 24.6789,
            "ordinate": 38.12345,
            "srid": 4326,
            "altitude": 219.22,
            "asrid": None,
        }

    def test_version_2(self):
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=2)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_version_2)

    def test_version_3(self):
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=3)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_version_3)

    def test_version_4(self):
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_version_4)

    def test_altitude_none(self):
        self.reference_ts.location["altitude"] = None
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_altitude)

    def test_no_altitude(self):
        del self.reference_ts.location["altitude"]
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_altitude)

    def test_altitude_zero(self):
        self.reference_ts.location["altitude"] = 0
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertIn("Altitude=0", outstring.getvalue())

    def test_location_none(self):
        self.reference_ts.location = None
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_location)

    def test_no_location(self):
        delattr(self.reference_ts, "location")
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_location)

    def test_precision_none(self):
        self.reference_ts.precision = None
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_precision)

    def test_no_precision(self):
        delattr(self.reference_ts, "precision")
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(outstring.getvalue(), tenmin_test_timeseries_file_no_precision)

    def test_precision_zero(self):
        self.reference_ts.precision = 0
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(
            outstring.getvalue(), tenmin_test_timeseries_file_zero_precision
        )

    def test_negative_precision(self):
        self.reference_ts.precision = -1
        outstring = StringIO()
        self.reference_ts.write(outstring, format=HTimeseries.FILE, version=4)
        self.assertEqual(
            outstring.getvalue(), tenmin_test_timeseries_file_negative_precision
        )


class HTimeseriesReadFilelikeTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries)
        s.seek(0)
        self.ts = HTimeseries(s)

    def test_length(self):
        self.assertEqual(len(self.ts.data), 5)

    def test_dates(self):
        np.testing.assert_array_equal(
            self.ts.data.index, pd.date_range("2008-02-07 11:20", periods=5, freq="10T")
        )

    def test_values(self):
        expected = np.array(
            [1141.00, 1142.01, 1154.02, float("NaN"), 1180.04], dtype=float
        )
        np.testing.assert_allclose(self.ts.data.values[:, 0].astype(float), expected)

    def test_flags(self):
        expected = np.array(["", "MISS", "", "", ""])
        np.testing.assert_array_equal(self.ts.data.values[:, 1], expected)


class HTimeseriesReadFilelikeMetadataOnlyTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries_file_version_4)
        s.seek(0)
        self.ts = HTimeseries(
            s, start_date="1971-01-01 00:00", end_date="1970-01-01 00:00"
        )

    def test_data_is_empty(self):
        pd.testing.assert_frame_equal(self.ts.data, standard_empty_dataframe)

    def test_metadata_was_read(self):
        self.assertEqual(self.ts.unit, "°C")


class HTimeseriesReadFilelikeWithMissingLocationButPresentAltitudeTestCase(TestCase):
    def setUp(self):
        s = StringIO("Altitude=55\n\n")
        self.ts = HTimeseries(s)

    def test_data_is_empty(self):
        pd.testing.assert_frame_equal(self.ts.data, standard_empty_dataframe)

    def test_has_altitude(self):
        self.assertEqual(self.ts.location["altitude"], 55)

    def test_has_no_abscissa(self):
        self.assertFalse("abscissa" in self.ts.location)


class HTimeseriesReadWithStartDateAndEndDateTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries)
        s.seek(0)
        self.ts = HTimeseries(
            s,
            start_date=dt.datetime(2008, 2, 7, 11, 30),
            end_date=dt.datetime(2008, 2, 7, 11, 55),
        )

    def test_length(self):
        self.assertEqual(len(self.ts.data), 3)

    def test_dates(self):
        np.testing.assert_array_equal(
            self.ts.data.index, pd.date_range("2008-02-07 11:30", periods=3, freq="10T")
        )

    def test_values(self):
        np.testing.assert_allclose(
            self.ts.data.values[:, 0].astype(float),
            np.array([1142.01, 1154.02, float("NaN")]),
        )

    def test_flags(self):
        np.testing.assert_array_equal(
            self.ts.data.values[:, 1], np.array(["MISS", "", ""])
        )


class HTimeseriesReadWithStartDateTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries)
        s.seek(0)
        self.ts = HTimeseries(s, start_date=dt.datetime(2008, 2, 7, 11, 45))

    def test_length(self):
        self.assertEqual(len(self.ts.data), 2)

    def test_dates(self):
        np.testing.assert_array_equal(
            self.ts.data.index, pd.date_range("2008-02-07 11:50", periods=2, freq="10T")
        )

    def test_values(self):
        np.testing.assert_allclose(
            self.ts.data.values[:, 0].astype(float), np.array([float("NaN"), 1180.04])
        )

    def test_flags(self):
        np.testing.assert_array_equal(self.ts.data.values[:, 1], np.array(["", ""]))


class HTimeseriesReadWithEndDateTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries)
        s.seek(0)
        self.ts = HTimeseries(s, end_date=dt.datetime(2008, 2, 7, 11, 50))

    def test_length(self):
        self.assertEqual(len(self.ts.data), 4)

    def test_dates(self):
        np.testing.assert_array_equal(
            self.ts.data.index, pd.date_range("2008-02-07 11:20", periods=4, freq="10T")
        )

    def test_values(self):
        np.testing.assert_allclose(
            self.ts.data.values[:, 0].astype(float),
            np.array([1141.00, 1142.01, 1154.02, float("NaN")]),
        )

    def test_flags(self):
        np.testing.assert_array_equal(
            self.ts.data.values[:, 1], np.array(["", "MISS", "", ""])
        )


class HTimeseriesReadFileFormatTestCase(TestCase):
    def setUp(self):
        s = StringIO(tenmin_test_timeseries_file_version_4)
        s.seek(0)
        self.ts = HTimeseries(s)

    def test_unit(self):
        self.assertEqual(self.ts.unit, "°C")

    def test_title(self):
        self.assertEqual(self.ts.title, "A test 10-min time series")

    def test_comment(self):
        self.assertEqual(
            self.ts.comment,
            textwrap.dedent(
                """\
                This timeseries is extremely important
                because the comment that describes it
                spans five lines.

                These five lines form two paragraphs."""
            ),
        )

    def test_timezone(self):
        self.assertEqual(self.ts.timezone, "EET (UTC+0200)")

    def test_time_step(self):
        self.assertEqual(self.ts.time_step, "10,0")

    def test_timestamp_rounding(self):
        self.assertEqual(self.ts.timestamp_rounding, "0,0")

    def test_timestamp_offset(self):
        self.assertEqual(self.ts.timestamp_offset, "0,0")

    def test_variable(self):
        self.assertEqual(self.ts.variable, "temperature")

    def test_precision(self):
        self.assertEqual(self.ts.precision, 1)

    def test_abscissa(self):
        self.assertAlmostEqual(self.ts.location["abscissa"], 24.678900, places=6)

    def test_ordinate(self):
        self.assertAlmostEqual(self.ts.location["ordinate"], 38.123450, places=6)

    def test_srid(self):
        self.assertEqual(self.ts.location["srid"], 4326)

    def test_altitude(self):
        self.assertAlmostEqual(self.ts.location["altitude"], 219.22, places=2)

    def test_asrid(self):
        self.assertTrue(self.ts.location["asrid"] is None)

    def test_length(self):
        self.assertEqual(len(self.ts.data), 5)

    def test_dates(self):
        np.testing.assert_array_equal(
            self.ts.data.index, pd.date_range("2008-02-07 11:20", periods=5, freq="10T")
        )

    def test_values(self):
        np.testing.assert_allclose(
            self.ts.data.values[:, 0].astype(float),
            np.array([1141.0, 1142.0, 1154.0, float("NaN"), 1180.0]),
        )

    def test_flags(self):
        np.testing.assert_array_equal(
            self.ts.data.values[:, 1], np.array(["", "MISS", "", "", ""])
        )


class HTimeseriesReadTimestampRoundingNoneTestCase(TestCase):
    def setUp(self):
        str1 = tenmin_test_timeseries_file_version_4.replace(
            "Timestamp_rounding=0,0", "Timestamp_rounding=None"
        ).replace("Timestamp_offset=0,0", "Timestamp_offset=None")
        s = StringIO(str1)
        s.seek(0)
        self.ts = HTimeseries(s)

    def test_timestamp_rounding(self):
        self.assertIsNone(self.ts.timestamp_rounding)

    def test_timestamp_offset(self):
        self.assertIsNone(self.ts.timestamp_offset)


class HTimeseriesAutoDetectFormatTestCase(TestCase):
    def test_auto_detect_text_format(self):
        self.assertEqual(
            HTimeseries()._auto_detect_format(StringIO(tenmin_test_timeseries)),
            HTimeseries.TEXT,
        )

    def test_auto_detect_file_format(self):
        self.assertEqual(
            HTimeseries()._auto_detect_format(
                StringIO(tenmin_test_timeseries_file_version_4)
            ),
            HTimeseries.FILE,
        )
