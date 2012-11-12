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

import django.contrib.auth
import logging
import json

from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Max, Min
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from monitor.analysis import *
from monitor.models import Reading, Station
from monitor.util import *
from powermon.settings import *
from types import *

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
JSON_MIMETYPE = 'application/json'
STATION_COOKIE = "powermon_station"

logger = logging.getLogger(__name__)


class StationForm(forms.Form):
  """Describes a station selection form."""
  station_id = forms.ChoiceField(
    label='Station',
    choices=queryset_to_list(Station.objects.all(), 'id', 'name'))


def index(request):
  """Handles the root/index URI by redirecting to the usage summary."""
  return redirect(usage)


def logout(request):
  """Logs the current user out of the application."""
  django.contrib.auth.logout(request)
  return redirect(logout_success)


def logout_success(request):
  """Displays a logout success message."""
  return render_to_response('logout_success.html', {}, context_instance=RequestContext(request))


@csrf_exempt
def record(request):
  """Records a reading provided by a power monitoring station."""
  if request.method != 'POST':
    return HttpResponse(request.method + ' not allowed.', status=405)

  station = None
  station_id = request.POST['id']
  try:
    station = Station.objects.get(id=station_id)
  except Station.DoesNotExist:
    logger.warn('Cannot record data for non-existent station ' + station_id)
    return HttpResponseServerError('Station %s does not exist.' % station_id)

  reading = Reading()
  reading.station = station
  reading.timestamp = now()
  reading.ip_address = request.META['REMOTE_ADDR']
  reading.watts = request.POST['w']
  reading.volts = request.POST['v']
  reading.amps = request.POST['a']
  reading.watt_hours = request.POST['wh']
  reading.power_factor = request.POST['pf']
  reading.frequency = request.POST['frq']
  reading.volt_amps = request.POST['va']
  reading.relay_status = request.POST['rnc']
  reading.power_cycle = request.POST['pcy']
  reading.save()

  message = 'Recorded %s' % reading
  logger.info(message)
  return HttpResponse(message)

@user_passes_test(has_data_access_permission)
def select_station(request):
  """Handles selection of the station for which data summary and analysis views are generated.
  The selected station is persisted via client-side coookie."""
  if request.method == 'POST':
    form = StationForm(request.POST)
    if form.is_valid():
      response = redirect(usage)
      response.set_cookie(STATION_COOKIE, form.cleaned_data['station_id'])
      return response
  else:
    form = StationForm()
  return render_to_response('select_station.html',
    {
      'form': form
    },
    context_instance=RequestContext(request))


@user_passes_test(has_data_access_permission)
def usage(request):
  """Generates a summary of power usage data for a particular station."""
  station = None
  if 'station_name' in request.GET:
    station = get_object_or_404(Station, name=request.GET['station_name'])
  else:
    station_id = None
    if 'station_id' in request.POST:
      station_id = request.POST['station_id']
    elif STATION_COOKIE in request.COOKIES:
      station_id = request.COOKIES[STATION_COOKIE]
    if not station_id:
      return redirect(select_station)
    station = get_object_or_404(Station, id=station_id)
  end = now()
  interval = timedelta(7)
  start = end - interval
  readings = get_readings(station.id, start, end)
  if len(readings) == 0:
    return render_to_response('nodata.html', {'station': station}, context_instance=RequestContext(request))

  energy_series = energy_timeseries(readings)
  median_usage = 'ERR'
  if len(energy_series) > 0:
     median_usage = median(energy_series) * 24 / 1000
  return render_to_response('usage.html',
    {
      'station': station,
      'stations': '|'.join([s.id for s in Station.objects.all()]),
      'median_kwh_day': median_usage,
      'kwh_tot': total_kWh(readings),
      'w_max' : max(r.watts for r in readings),
      'w_min' : min(r.watts for r in readings)
    },
    context_instance=RequestContext(request))


@user_passes_test(has_data_access_permission)
def flotseries(request, stations, variables, period, end=None):
  """Produces a JSON list of time series for one or more power monitoring variables and one or more stations.
  The stations and variables parameters are pipe-delimited lists of station IDs and power variables
  (watts, amps,etc), respectively.
  The end parameter is optional and is specified to mark the right-hand side of the time interval, otherwise the
  current time is used. Times nust be in ISO format, 'YYYY-mm-ddTHH:MM:SS'.
  Periods are simple strings of the format nX where n is an integer and X is either h for hours or d for days.
  The time interval for the data set is the interval [t - period, t], inclusive, where t is either end or the
  current time.
  The JSON string conforms to that required by the flot API, http://flot.googlecode.com/svn/trunk/API.txt"""
  if end is None:
    end = now()
  else:
    end = datetime.strptime(end, ISO_FORMAT)
  start = end - parse_period(period)
  stationlist = stations.split('|')
  fieldlist = variables.split('|')
  flot_data = []
  for station_id in stationlist:
    station = Station.objects.get(pk=station_id)
    readings = get_readings(station_id, start, end)
    series = timeseries(readings, *fieldlist)
    for i in range(len(fieldlist)):
      flot_data.append({'data': series[i], 'label': "%s - %s" % (fieldlist[i], station.name)})
  return HttpResponse(json.dumps(flot_data), content_type=JSON_MIMETYPE)


def status(request):
  """Presents a status page that provides a suitable target for health checks."""
  reading_map = {}
  end = now()
  interval = timedelta(minutes=STATUS_TIMEOUT)
  start = end - interval
  zero_count = 0
  for station in Station.objects.all():
    readings = get_readings(station.id, start, end)
    if len(readings) == 0:
      zero_count += 1
    reading_map[station.name] = readings
  result = 'OK'
  code = 200
  if zero_count == len(reading_map):
    result = 'ERROR: no stations have reported data in the past %s' % interval
    code = 500
  elif zero_count > 0:
    result = 'WARN: at least one station has not reported data in the past %s' % interval
    code = 306
  message = '%s\n\nStation reading counts in past %s\n' % (result, interval)
  message += '\n'.join(['%s\t\t%s' % (k, len(v)) for (k, v) in reading_map.items()])
  return HttpResponse(message, 'text/plain', code)


@user_passes_test(has_data_access_permission)
def leaders(request):
  """Provides a view of stations sorted by increasing power usage for various time periods."""
  end = now()
  leaders = {}
  period = ('24h', '7d', '30d', None)
  for p in period:
    if p is None:
      stations = Station.objects.all()
    else:
      start = end - parse_period(p)
      stations = Station.objects.filter(
        reading__timestamp__gte=start,
        reading__timestamp__lte=end)
    leaders[p] = stations.annotate(
      power_max=Max('reading__watt_hours'),
      power_min=Min('reading__watt_hours'))
    # Add computed attribute to each station
    for row in leaders[p]:
      setattr(row, 'total_kwh', (row.power_max - row.power_min) / 1000)
    leaders[p] = sorted(leaders[p], key=lambda r: r.total_kwh)
  return render_to_response('leaders.html',
    {
      'leaders_day': leaders['24h'],
      'leaders_week': leaders['7d'],
      'leaders_month': leaders['30d'],
      'leaders_overall': leaders[None],
    },
    context_instance=RequestContext(request))
