=======
History
=======

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
