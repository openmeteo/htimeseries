import datetime as dt
from configparser import ParsingError
from io import SEEK_CUR, SEEK_END, SEEK_SET, StringIO, UnsupportedOperation

import numpy as np
import pandas as pd
from textbisect import text_bisect_left, text_bisect_right


class _BacktrackableFile(object):
    def __init__(self, fp):
        self.fp = fp
        self.line_number = 0
        self.next_line = None

    def readline(self):
        if self.next_line is None:
            self.line_number += 1
            result = self.fp.readline()
        else:
            result = self.next_line
            self.next_line = None
        return result

    def backtrack(self, line):
        self.next_line = line

    def read(self, size=None):
        return self.fp.read() if size is None else self.fp.read(size)

    def __getattr__(self, name):
        return getattr(self.fp, name)


class _FilePart(object):
    """A wrapper that views only a subset of the wrapped filelike object.

    When it is created, three mandatory parameters are passed: a filelike
    object, startpos and endpos. This wrapper then acts as a filelike object of
    size endpos+1-startpos, which views the part of the wrapped object between
    startpos and endpos.
    """

    def __init__(self, stream, startpos, endpos):
        self.startpos = startpos
        self.endpos = endpos
        self.stream = stream
        if self.stream.tell() < self.startpos:
            self.stream.seek(self.startpos)
        if self.stream.tell() > self.endpos + 1:
            self.stream.seek(0, SEEK_END)

    def read(self, size=-1):
        max_available_size = self.endpos + 1 - self.stream.tell()
        size = min(size, max_available_size)
        if size == -1:
            size = max_available_size
        return self.stream.read(size)

    def readline(self, size=-1):
        max_available_size = self.endpos + 1 - self.stream.tell()
        size = min(size, max_available_size)
        return self.stream.readline(size)

    def seek(self, offset, whence=SEEK_SET):
        if whence == SEEK_SET:
            if offset < 0:
                raise ValueError("negative seek position {}".format(offset))
            targetpos = self.startpos + offset
            if targetpos > self.endpos + 1:
                targetpos = self.endpos + 1
            self.stream.seek(targetpos)
            # It might seem more reasonable to return targetpos -
            # self.startpos, but we choose to do the same thing Python does in
            # other cases; if you do f.seek(VERY_LARGE), it returns VERY_LARGE,
            # even if it is larger than the size of the file.
            return offset
        elif whence == SEEK_CUR:
            # Do nothing by simply calling the wrapped (which requires that
            # offset be zero).
            return self.stream.seek(offset, SEEK_CUR)
        elif whence == SEEK_END:
            if offset != 0:
                return UnsupportedOperation("can't do nonzero cur-relative seeks")
            return self.stream.seek(self.endpos)
        else:
            assert False

    def tell(self):
        return self.stream.tell() - self.startpos

    def __getattr__(self, name):
        return getattr(self.stream, name)


class _MetadataWriter:
    def __init__(self, f, htimeseries, version=4):
        self.version = version
        self.htimeseries = htimeseries
        self.f = f

    def write_meta(self):
        if self.version == 2:
            self.f.write("Version=2\r\n")
        self.write_simple("unit")
        self.write_count()
        self.write_simple("title")
        self.write_comment()
        self.write_simple("timezone")
        self.write_simple("time_step")
        self.write_timestamp_rounding()
        self.write_timestamp_offset()
        self.write_simple("interval_type")
        self.write_simple("variable")
        self.write_simple("precision")
        self.write_location()
        self.write_altitude()

    def write_simple(self, parm):
        value = getattr(self.htimeseries, parm, None)
        if value is not None:
            self.f.write("{}={}\r\n".format(parm.capitalize(), value))

    def write_count(self):
        self.f.write("Count={}\r\n".format(len(self.htimeseries.data)))

    def write_comment(self):
        if hasattr(self.htimeseries, "comment"):
            for line in self.htimeseries.comment.splitlines():
                self.f.write("Comment={}\r\n".format(line))

    def write_timestamp_rounding(self):
        timestamp_rounding_name = (
            self.version >= 4 and "Timestamp_rounding" or "Nominal_offset"
        )
        if hasattr(self.htimeseries, "timestamp_rounding"):
            self.f.write(
                "{}={}\r\n".format(
                    timestamp_rounding_name, self.htimeseries.timestamp_rounding
                )
            )

    def write_timestamp_offset(self):
        timestamp_offset_name = (
            self.version >= 4 and "Timestamp_offset" or "Actual_offset"
        )
        if hasattr(self.htimeseries, "timestamp_offset"):
            self.f.write(
                "{}={}\r\n".format(
                    timestamp_offset_name, self.htimeseries.timestamp_offset
                )
            )

    def write_location(self):
        if self.version <= 2 or not getattr(self.htimeseries, "location", None):
            return
        self.f.write(
            "Location={:.6f} {:.6f} {}\r\n".format(
                *[
                    self.htimeseries.location[x]
                    for x in ["abscissa", "ordinate", "srid"]
                ]
            )
        )

    def write_altitude(self):
        no_altitude = (
            (self.version <= 2)
            or not getattr(self.htimeseries, "location", None)
            or ("altitude" not in self.htimeseries.location)
            or (not self.htimeseries.location["altitude"])
        )
        if no_altitude:
            return
        altitude = self.htimeseries.location["altitude"]
        asrid = (
            self.htimeseries.location["asrid"]
            if "asrid" in self.htimeseries.location
            else None
        )
        fmt = (
            "Altitude={altitude:.2f} {asrid}\r\n"
            if asrid
            else "Altitude={altitude:.2f}\r\n"
        )
        self.f.write(fmt.format(altitude=altitude, asrid=asrid))


class _MetadataReader:
    def __init__(self, f):
        f = _BacktrackableFile(f)

        # Check if file contains headers
        first_line = f.readline()
        f.backtrack(first_line)
        if isinstance(first_line, bytes):
            first_line = first_line.decode("utf-8-sig")
        has_headers = not first_line[0].isdigit()

        # Read file, with its headers if needed
        self.meta = {}
        if has_headers:
            self.read_meta(f)

    def read_meta(self, f):
        """Read the headers of a file in file format and place them in the
        self.meta dictionary.
        """
        if not isinstance(f, _BacktrackableFile):
            f = _BacktrackableFile(f)

        try:
            (name, value) = self.read_meta_line(f)
            while name:
                name = name == "nominal_offset" and "timestamp_rounding" or name
                name = name == "actual_offset" and "timestamp_offset" or name
                method_name = "get_{}".format(name)
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(name, value)
                name, value = self.read_meta_line(f)
                if not name and not value:
                    break
        except ParsingError as e:
            e.args = e.args + (f.line_number,)
            raise

    def get_unit(self, name, value):
        self.meta[name] = value

    get_title = get_unit
    get_timezone = get_unit
    get_variable = get_unit

    def get_time_step(self, name, value):
        minutes, months = self.read_minutes_months(value)
        self.meta[name] = "{},{}".format(minutes, months)

    get_timestamp_rounding = get_time_step
    get_timestamp_offset = get_time_step

    def get_interval_type(self, name, value):
        value = value.lower()
        if value not in ("sum", "average", "maximum", "minimum", "vector_average"):
            raise ParsingError(("Invalid interval type"))
        self.meta[name] = value

    def get_precision(self, name, value):
        try:
            self.meta[name] = int(value)
        except ValueError as e:
            raise ParsingError(e.args)

    def get_comment(self, name, value):
        if "comment" in self.meta:
            self.meta["comment"] += "\n"
        else:
            self.meta["comment"] = ""
        self.meta["comment"] += value

    def get_location(self, name, value):
        if "location" not in self.meta:
            self.meta["location"] = {}
        try:
            items = value.split()
            self.meta["location"]["abscissa"] = float(items[0])
            self.meta["location"]["ordinate"] = float(items[1])
            self.meta["location"]["srid"] = int(items[2])
        except (IndexError, ValueError):
            raise ParsingError("Invalid location")

    def get_altitude(self, name, value):
        if "location" not in self.meta:
            self.meta["location"] = ""
        try:
            items = value.split()
            self.meta["location"]["altitude"] = float(items[0])
            self.meta["location"]["asrid"] = int(items[1]) if len(items) > 1 else None
        except (IndexError, ValueError):
            raise ParsingError("Invalid altitude")

    def read_minutes_months(self, s):
        """Return a (minutes, months) tuple after parsing a "M,N" string.
        """
        try:
            (minutes, months) = [int(x.strip()) for x in s.split(",")]
            return minutes, months
        except Exception:
            raise ParsingError(('Value should be "minutes, months"'))

    def read_meta_line(self, f):
        """Read one line from a file format header and return a (name, value)
        tuple, where name is lowercased. Returns ('', '') if the next line is
        blank. Raises ParsingError if next line in f is not a valid header
        line."""
        line = f.readline()
        if isinstance(line, bytes):
            line = line.decode("utf-8-sig")
        name, value = "", ""
        if line.isspace():
            return (name, value)
        if line.find("=") > 0:
            name, value = line.split("=", 1)
            name = name.rstrip().lower()
            value = value.strip()
        name = "" if any([c.isspace() for c in name]) else name
        if not name:
            raise ParsingError("Invalid file header line")
        return (name, value)


class HTimeseries:
    TEXT = "TEXT"
    FILE = "FILE"

    def __init__(self, data=None, **kwargs):
        if data is None:
            self._read_filelike(StringIO())
        elif isinstance(data, pd.DataFrame):
            self.data = data
        else:
            self._read_filelike(data, **kwargs)

    def _read_filelike(self, f, format=None, start_date=None, end_date=None):
        # Auto detect format if needed
        if format is None:
            format = self._auto_detect_format(f)

        # If file format, get the metadata
        if format == self.FILE:
            self.__dict__.update(_MetadataReader(f).meta)

        # Determine start_date and end_date as ISO8601 strings
        start_date = "0001-01-01 00:00" if start_date is None else start_date
        end_date = "9999-12-31 00:00" if end_date is None else end_date
        if isinstance(start_date, dt.datetime):
            start_date = start_date.strftime("%Y-%m-%d %H:%M")
        if isinstance(end_date, dt.datetime):
            end_date = end_date.strftime("%Y-%m-%d %H:%M")

        # Determine the subset of the file that is of interest
        lo = f.tell()
        key = lambda x: x.split(",")[0]  # NOQA
        endpos = text_bisect_right(f, end_date, lo=lo, key=key) - 1
        startpos = text_bisect_left(f, start_date, lo=lo, key=key)
        f2 = _FilePart(f, startpos, endpos)

        # Read it
        self.data = pd.read_csv(
            f2,
            parse_dates=[0],
            names=("date", "value", "flags"),
            usecols=("date", "value", "flags"),
            index_col=0,
            header=None,
            converters={"flags": lambda x: x},
            dtype={"value": np.float64},
        )

    def _auto_detect_format(self, f):
        original_position = f.tell()
        result = self._auto_detect_format_without_restoring_file_position(f)
        f.seek(original_position)
        return result

    def _auto_detect_format_without_restoring_file_position(self, f):
        line = self._get_first_nonempty_line(f)
        if line and not line[0].isdigit():
            return self.FILE
        else:
            return self.TEXT

    def _get_first_nonempty_line(self, f):
        for line in f:
            if line.strip():
                return line
        return ""

    def write(self, f, format=TEXT, version=4):
        if format == self.FILE:
            _MetadataWriter(f, self, version=version).write_meta()
            f.write("\r\n")

        if self.data.empty:
            return
        float_format = "%f"
        if hasattr(self, "precision") and self.precision is not None:
            if self.precision >= 0:
                float_format = "%.{}f".format(self.precision)
            else:
                float_format = "%.0f"
                datacol = self.data.columns[0]
                m = 10 ** (-self.precision)
                self.data[datacol] = np.rint(self.data[datacol] / m) * m
        self.data.to_csv(
            f,
            float_format=float_format,
            header=False,
            mode="wb",
            line_terminator="\r\n",
            date_format="%Y-%m-%d %H:%M",
        )
