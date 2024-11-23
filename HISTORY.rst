=======
History
=======

8.0.0 (2024-11-23)
==================

- Upgraded pandas from version 1 to 2.

7.0.0 (2024-04-14)
==================

- When saving in file format, the Timezone= parameter now merely
  contains +HHmm.
- The HTimeseries.timezone attribute has been abolished; use
  HTimeseries.data.index.tz instead.
- When initialized with a dataframe, it checks that the index is aware.

6.0.3 (2024-03-21)
==================

- Fixed error with unspecified time zone in HTimeseries objects created
  empty.  Now creating an empty object with ``HTimeseries()`` assumes
  ``default_tzinfo=ZoneInfo("UTC")``.

6.0.2 (2023-12-22)
==================

- Fixed crash when reading csv with aware timestamps.

6.0.1 (2023-12-19)
==================

- Fixed crash when reading csv with only a date column.

6.0.0 (2023-12-14)
==================

- Python 3.9 is now required (the reason for this is that
  backports.zoneinfo is behaving differently from zoneinfo).
- Only pandas>=1.5,<2  is now supported. Pandas<1.5 probably did not
  work in 5.0.0 either, but it had not been discovered. Pandas>=2
  handles ambiguous times differently and is therefore still
  unsupported.
- Increased CSV reading speed by two orders of magnitude.

5.0.0 (2023-11-21)
==================

- Removed compatibility with pandas<1. pandas 1 and 2 are now supported.
  This helps avoid an error when reading a data file spanning a time
  interval that contains a change to or from DST.

4.0.2 (2022-11-27)
==================

- Worked around an old Pandas bug related to time zones
  (https://github.com/pandas-dev/pandas/issues/11736) in order to
  maintain compatibility with Pandas 0.23 (the bug was fixed in Pandas
  0.24). 

4.0.1 (2022-11-27)
==================

- Fixed packaging error where it didn't install dependency
  backports.zoneinfo on Python<3.9.

4.0.0 (2022-11-22)
==================

- The timestamps of the dataframe index are now aware. When initializing
  a ``HTimeseries`` object with a dataframe, the dataframe index
  timestamps must be aware. When initializing with a filelike object,
  either the filelike object must contain a ``timezone`` header or the
  new ``default_tzinfo`` parameter must be specified.

3.1.1 (2020-12-29)
==================

- Fixed incompatibility with pandas 1.2.

3.1.0 (2020-12-17)
==================

- When reading a time series from a file-like object, it is now
  permitted for it to not have a flags column. In this case, an empty
  flags column is automatically added to the HTimeseries object.

3.0.0 (2020-02-23)
==================

- Only Python>=3.7 is now supported.
- When reading or writing a time series, it now checks that there are no
  duplicate timestamps and raises an exception if there are.

2.0.5 (2020-01-15)
==================

- Fix pandas dependency to use pandas<1, so that Python 3.5
  compatibility is kept.

2.0.4 (2020-01-08)
==================

- Fixed crash when saving in version 2 and the time step was a mere "M"
  or "Y" without multiplier.

2.0.3 (2020-01-05)
==================

- Default version when writing file is now latest.

2.0.1 (2020-01-04)
==================

- Fixed error when the time step was empty.

2.0.0 (2020-01-04)
==================

- Changed the way the time step is specified. Instead of
  "minutes,months", it is now a pandas "frequency" offset specification
  such as "5min" or "3M".
- The timestamp_offset and timestamp_rounding parameters have been
  abolished.

1.1.2 (2019-07-18)
==================

- Fixed some altitude-related bugs: 1) It would crash when trying to
  read a file that specified altitude but not location; 2) it wouldn't
  write altitude to the file it the altitude was zero.

1.1.1 (2019-06-12)
==================

- Fixed crash when Timestamp_rounding=None or Timestamp_offset=None.

1.1.0 (2019-06-08)
==================

- Added TzinfoFromString utility (moved in here from pthelma).

1.0.1 (2019-06-06)
==================

- Fixed error in the README (which prevented 1.0.0 from being uploaded
  to PyPi).

1.0.0 (2019-06-06)
==================

- API change: .read() is gone, now we use a single overloaded
  constructor; either HTimeseries() or HTimeseries(dataframe) or 
  HTimeseries(filelike).
- The columns and dtypes of .data are now standardized and properly
  created even for empty objects (created with HTimeseries()).

0.2.0 (2019-04-09) 
==================

- Auto detect format when reading a file

0.1.0 (2019-01-14)
==================

- Initial release
