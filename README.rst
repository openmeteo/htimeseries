=========================================================
htimeseries - Hydrological and meteorological time series
=========================================================


.. image:: https://img.shields.io/pypi/v/htimeseries.svg
        :target: https://pypi.python.org/pypi/htimeseries

.. image:: https://img.shields.io/travis/openmeteo/htimeseries.svg
        :target: https://travis-ci.org/openmeteo/htimeseries

.. image:: https://codecov.io/github/openmeteo/htimeseries/coverage.svg
        :target: https://codecov.io/gh/openmeteo/htimeseries
        :alt: Coverage

.. image:: https://pyup.io/repos/github/openmeteo/htimeseries/shield.svg
         :target: https://pyup.io/repos/github/openmeteo/htimeseries/
         :alt: Updates

This module provides the HTimeseries class, which is a layer on top of
pandas, offering a little more functionality.

Introduction
============

::

    ts = HTimeseries()

This creates a ``HTimeseries`` object, whose ``data`` attribute is a
pandas time series or dataframe with a datetime index. Besides ``data``,
it can have other attributes which serve as the time series' metadata.
There are also several utility methods described below.

Reference
=========

**HTimeseries(data=None)**

Creates a ``HTimeseries`` object. ``data`` can be a pandas time series
or dataframe indexed by datetime or a file-like object. If it is a
pandas object, it becomes the value of the ``data`` attribute. If it is
a file-like object, the time series is read from it using the
``.read()`` method.

**.data**

A pandas time series or dataframe indexed by datetime. This contains the
data of the time series.

classmethod **.read(f, format=HTimeseries.TEXT, start_date=None, end_date=None)**

Reads filelike object ``f`` that contains a time series and returns a
``HTimeseries`` object. There must be no newline translation in ``f``
(open it with ``open(..., newline='\n')``. If ``start_date`` and
``end_date`` are specified, it skips rows outside the range.

The contents of ``f`` can be in text format or file format (see
"formats" below). This is specified by the ``format`` parameter.  If
reading in text format (``format=HTimeseries.TEXT``), the returned
object just has the ``data`` attribute set. If reading in file format
(``format=HTimeseries.FILE``), the returned object also has attributes
``unit``, ``title``, ``comment``, ``time_zone``, ``time_step``,
``timestamp_rounding``, ``timestamp_offset``, ``interval_type``,
``variable``, ``precision`` and ``location``. For the meaning of these
attributes, see section "File format" below.

These attributes are purely informational. In particular, ``time_step``
and the other time-step-related attributes don't necessarily mean that
the pandas object will have a related time step (also called
"frequency"). In fact, raw time series may be irregular but actually
have a time step. For example, a ten-minute time series might end in
:10, :20, etc., but at some point there might be an irregularity and it
could continue with :31, :41, etc.  Strictly speaking, such a time
series has an irregular step. However, when stored in a database,
specifying that its time step is ten minutes (because that's what it is,
ten minutes with irregularities) can help people who browse or search
the database contents.

The ``location`` attribute is a dictionary that has items ``abscissa``,
``ordinate``, ``srid``, ``altitude``, and ``asrid``.

**.write(f, format=HTimeseries.TEXT, version=4)**

Writes the time series to filelike object ``f``. In accordance with the
:ref:`text format specification <textformat>`, time series are written
using the CR-LF sequence to terminate lines.  Care should be taken that
``f``, or any subsequent operations on ``f``, do not perform text
translation; otherwise it may result in lines being terminated with
CR-CR-LF. If ``f`` is a file, it should have been opened in binary mode.

``version`` is ignored unless ``format=HTimeseries.FILE``.

Formats
=======

There are two formats: the *text format* is generic text format, without
metadata; the *file format* is like the text format, but additionally
contains headers with metadata.

.. _textformat:

Text format
-----------

The text format for a time series is us-ascii, one line per record,
like this:

    2006-12-23 18:34,18.2,RANGE

The three fields are comma-separated and must always exist.  In the date
field, the time may be missing. The character that separates the date
from the time may be either a space or a lower case ``t``, or a capital
``T`` (this module produces text format using a space as date separator,
but can read text format that uses ``t`` or ``T``). The second field
always uses a dot as the decimal separator and may be empty.  The third
field is usually empty but may contain a list of space-separated flags.
The line separator should be the CR-LF sequence used in MS-DOS and
Windows systems. Code that produces text format should always use CR-LF
to end lines, but code that reads text format should be able to also
read lines that end in LF only, as well as CR-CR-LF (for reasons
explained in the ``write()`` function above).

In order to improve performance in file writes, the maximum length of
each time series record line is limited to 255 characters.

Flags should be encoded in ASCII; there must be no characters with
code greater than 127.

.. _fileformat:

File format
-----------

The file format is like this::

    Version=2
    Title=My timeseries
    Unit=°C

    2006-12-23 18:34,18.2,RANGE
    2006-12-23 18:44,18.3,

In other words, the file format consists of a header that specifies
parameters in the form ``Parameter=Value``, followed by a blank line,
followed by the timeseries in text format. The same conventions for line
terminators apply here as for the text format. The encoding of the
header section is UTF-8.

Client and server software should recognize UTF-8 files with or without
UTF-8 BOM (Byte Order Mark) in the begining of file.  Writes may or may
not include the BOM, according OS. (Usually Windows software attaches
the BOM at the beginning of the file).

Parameter names are case insensitive.  There may be white space on
either side of the equal sign, which is ignored. Trailing white space on
the line is also ignored. A second equal sign is considered to be part
of the value. The value cannot contain a newline, but there is a way to
have multi-lined parameters explained in the Comment parameter below.
All parameters except Version are optional: either the value can be
blank or the entire ``Parameter=Value`` can be missing; the only
exception is the Comment parameter.

The parameters available are:

**Version**
  There are four versions:

  * Version 1 files are long obsolete. They did not have a header
    section.

  * Version 2 files must have ``Version=2`` as the first line of the
    file. All other parameters are optional. The file may not contain
    unrecognized parameters; software reading files with unrecognized
    parameters may raise an error.

  * Version 3 files do not have the *Version* parameter. At least one of
    the other parameters must be present. Unrecognized parameters are
    ignored when reading. The deprecated parameter names
    *Nominal_offset* and *Actual_offset* are used instead of the newer
    ones *Timestamp_rounding* and *Timestamp_offset*.

  * Version 4 files are the same as Version 3, except for the names of
    the parameters *Timestamp_rounding* and *Timestamp_offset*.

**Unit**
    A symbol for the measurement unit, like ``°C`` or ``mm``.

**Count**
    The number of records in the time series. If present, it need not be
    exact; it can be an estimate. Its primary purpose is to enable
    progress indicators in software that takes time to read large time
    series files. In order to determine the actual number of records,
    the records need to be counted.

**Title**
    A title for the time series.

**Comment**
    A multiline comment for the time series. Multiline comments are
    stored by specifying multiple adjacent Comment parameters, like
    this::

        Comment=This timeseries is extremely important
        Comment=because the comment that describes it
        Comment=spans five lines.
        Comment=
        Comment=These five lines form two paragraphs.

    The Comment parameter is the only parameter where a blank value is
    significant and indicates an empty line, as can be seen in the
    example above.

**Timezone**
    The time zone of the timestamps, in the format :samp:`{XXX}
    (UTC{+HHmm})`, where *XXX* is a time zone name and *+HHmm* is the
    offset from UTC. Examples are ``EET (UTC+0200)`` and ``VST
    (UTC-0430)``.

**Time_step**
    A comma-separated pair of integers; the number of minutes and months
    in the time step (one of the two mut be zero). If missing, the time
    series is without time step.

**Timestamp_rounding**
    A comma-separated pair of integers indicating the number of minutes
    and months that must be added to a round timestamp to get to the
    nominal timestamp.  For example, if an hourly time series has
    timestamps that end in :13, such as 01:13, 02:13, etc., then its
    rounding is 13 minutes, 0 months, i.e., ``(13, 0)``. Monthly time
    series normally have a nominal timestamp of ``(0, 0)``, the
    timestamps usually being of the form 2008-02-01 00:00, meaning
    "February 2008" and usually rendered by application software as "Feb
    2008" or "2008-02". Annual timestamps have a nominal timestamp which
    normally has 0 minutes, but may have nonzero months; for example, a
    common rounding in Greece is 9 months (0=January), which means that
    an annual timestamp is of the form 2008-10-01 00:00, normally
    rendered by application software as 2008-2009, and denoting the
    hydrological year 2008-2009.

    ``timestamp_rounding`` may be None, meaning that the timestamps can
    be irregular.

    *Timestamp_rounding* is named differently in older versions. See the
    *Version* parameter above for more information.

**Timestamp_offset**
    A comma-separated pair of integers indicating the number of minutes
    and months that must be added to the nominal timestamp to get to the
    actual timestamp. The timestamp offset for small time steps, such as
    up to daily, is usually zero, except if the nominal timestamp is the
    beginning of an interval, in which case the timestamp offset is
    equal to the length of the time step, so that the actual timestamp
    is the end of the interval. For monthly and annual time steps, the
    timestamp offset is usually 1 and 12 months respectively.  For a
    monthly time series, a timestamp offset of (-475, 1) means that
    2003-11-01 00:00 (often rendered as 2003-11) denotes the interval
    2003-10-31 18:05 to 2003-11-30 18:05.

    *Timestamp_offset* is named differently in older versions. See the
    *Version* parameter above for more information.

**Interval_type**
    Has one of the values ``sum``, ``average``, ``maximum``,
    ``minimum``, and ``vector_average``. If absent it means that the
    time series values are instantaneous, they do not refer to
    intervals.

**Variable**
    A textual description of the variable, such as ``Temperature`` or
    ``Precipitation``.

**Precision**
    The precision of the time series values, in number of decimal digits
    after the decimal separator. It can be negative; for example, a
    precision of -2 indicates values accurate to the hundred, such as
    100, 200, 300 etc.

**Location**, **Altitude**
    (Versions 3 and later.) *Location* is three numbers,
    space-separated: abscissa, ordinate, and EPSG SRID. *Altitude* is
    one or two space-separated numbers: the altitude and the EPSG SRID
    for altitude. The altitude SRID may be omitted.
