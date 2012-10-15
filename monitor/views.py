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
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from monitor.analysis import *
from monitor.models import Reading, Station
from monitor.util import *
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
  reading.timestamp = datetime.today()
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
  end = datetime.today()
  interval = timedelta(7)
  start = end - interval
  readings = get_readings(station.id, start, end)
  if len(readings) == 0:
    return render_to_response('nodata.html', {'station': station}, context_instance=RequestContext(request))
  return render_to_response('usage.html',
    {
      'station': station,
      'median_kwh_day': median(energy_timeseries(readings)) * 24 / 1000,
      'kwh_tot': total_kWh(readings),
      'w_max' : max(r.watts for r in readings),
      'w_min' : min(r.watts for r in readings)
    },
    context_instance=RequestContext(request))


@user_passes_test(has_data_access_permission)
def flotseries(request, station_id, fields, period, end=datetime.today()):
  """Produces a JSON list of time series, one for each field, for the given power monitoring station.
  The end parameter is optional and is specified to mark the right-hand side of the time interval, otherwise the
  current time is used. Times nust be in ISO format, 'YYYY-mm-ddTHH:MM:SS'.
  Periods are simple strings of the format nX where n is an integer and X is either h for hours or d for days.
  The time interval for the data set is the interval [t - period, t], inclusive, where t is either end or the
  current time.
  The JSON string conforms to that required by the flot API, http://flot.googlecode.com/svn/trunk/API.txt"""
  if type(end) is StringType:
    end = datetime.strptime(end, ISO_FORMAT)
  start = end - parse_period(period)
  fieldlist = fields.split('|')
  readings = get_readings(station_id, start, end)
  series = timeseries(readings, *fieldlist)
  flot_data = []
  for i in range(len(fieldlist)):
    flot_data.append({'data': series[i], 'label': fieldlist[i]})
  return HttpResponse(json.dumps(flot_data), content_type=JSON_MIMETYPE)
