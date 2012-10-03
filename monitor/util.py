#####################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
#####################################################################

import calendar
import inspect
import re
import time

from datetime import datetime,timedelta
from monitor.models import Reading

PERIOD_REGEX = re.compile(r'(\d+)([mhd])')


def queryset_to_list(queryset, *fields, **kwargs):
  """Converts a queryset to a list of n-tuples containing only the given fields from each model in the queryset
  with the option to permute values by a function.
  If a permutations keyword parameter is provided, it must be a map of field names to functions that take one argument.
  The result of function evaluation is used instead of the value itself in the generated list.
  If only two fields are specified, the return value is suitable for use as the choices parameter of the ChoiceField
  type of model and form objects."""
  items = []
  permutations = None
  if 'permutations' in kwargs:
    permutations = kwargs['permutations']
  else:
    permutations = {}
  value = 0
  for item in queryset:
    values = []
    for field in fields:
      previous = value
      value = getattr(item, field)
      if field in permutations:
        fun = permutations[field]
        argsize = len(inspect.getargspec(fun).args)
        if argsize == 1:
          value = fun(value)
        else:
          raise Exception('Expected permutation function that takes one argument but got %s' % argsize)
      values.append(value)
    items.append(tuple(values))
  return items


def parse_period(period):
  """Parses a time period of the form nX where n is an integer and X is one of m (minutes), h (hours), d (days).
  A timedelta object representing the period is returned."""
  match = PERIOD_REGEX.match(period)
  if not match: raise Exception('Invalid period ' + period)
  interval = int(match.group(1))
  unit = match.group(2)
  if unit == 'm':
    return timedelta(minutes=interval)
  elif unit == 'h':
    return timedelta(hours=interval)
  return timedelta(interval)


def epoch(dt):
  """Converts a Python datetime object in local time to milliseconds since the Unix epoch, midnight 1970-01-01 UTC."""
  return calendar.timegm(dt.timetuple()) * 1000


def get_readings(station_id, start, end):
  """Gets a sequence of power readings for the given station in the time interval [start, end]."""
  return Reading.objects.filter(station_id=station_id).filter(timestamp__gte=start).filter(timestamp__lte=end)

