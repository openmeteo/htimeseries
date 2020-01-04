=======
History
=======

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
