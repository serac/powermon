import numpy as np
from datetime import datetime, timedelta
from monitor.util import *


def timeseries(readings, *fields):
  """Converts a sequence of readings into a list of time series in each of the given variables.
  Each time series is a list of two-tuples (t, f(t)) where f is one of the fields in the power reading.
  The size of the returned list is equal to the number of fields given.
  Times are represented as UTC Unix timestamps, i.e. milliseconds since midnight 1970-01-01."""
  permutations = {
    'timestamp': epoch
  }
  rows = queryset_to_list(readings, *(('timestamp',) + fields), permutations=permutations)
  series = []
  for i in range(len(fields)):
    series.append([(row[0], row[i+1]) for row in rows])
  return series


def energy_timeseries(readings):
  """Creates a time series of energy consumption in watt-hours per hour."""
  first = readings[0]
  last = readings[len(readings) - 1]
  period = timedelta(hours=1)
  series = []
  current = first
  for reading in readings:
    if reading.timestamp - current.timestamp >= period:
      series.append((epoch(reading.timestamp), reading.watt_hours - current.watt_hours))
      current = reading
  return series


def to_nparray(nsequence):
  """Converts a n-dimensional sequence of integers into a numpy array."""
  return np.array(nsequence, dtype=np.int32)


def median(timeseries):
  """Computes the median value of the y-coordinate of a time series."""
  return np.median(to_nparray(timeseries)[:,1])


def median_watts(readings):
  """Computes the median watts over all given readings."""
  return median(timeseries(readings, 'watts')[0])


def total_kWh(readings):
  """Computes the total kWh used over all given readings.
  Readings are assumed to be ordered in ascending chronological order, which is the natural order for readings."""
  return (readings[len(readings) - 1].watt_hours - readings[0].watt_hours) / 1000

