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

from datetime import datetime, timedelta
from django.test import TestCase
from monitor.models import Reading, Station
from monitor.analysis import *
from monitor.util import *


class AnalysisTest(TestCase):
  def setUp(self):
    station = Station.objects.create(id='12345', name='test')
    timestamp = datetime.today()
    delta = timedelta(seconds=1)
    # list of (watts, watt_hours)
    data = ((10, 21000), (12, 22000), (15, 24000), (17, 25000), (19, 26000))
    self.readings = []
    address = '127.0.0.1'
    for datum in data:
      self.readings.append(
        Reading.objects.create(
        station=station,
        ip_address=address,
        timestamp=timestamp,
        watts=datum[0],
        volts=0,
        amps=0,
        watt_hours=datum[1],
        power_factor=0,
        frequency=0,
        volt_amps=0,
        relay_status=0,
        power_cycle=0))
      timestamp += delta

  def test_total_kWh(self):
    self.assertEqual(total_kWh(self.readings), 5)

  def test_median_watts(self):
    self.assertEqual(median_watts(self.readings), 15)


class UtilTest(TestCase):
  def test_epoch(self):
    test_date = datetime.strptime('2012-01-01 13:00:05', '%Y-%m-%d %H:%M:%S')
    self.assertEquals(epoch(test_date), 1325440805000 - 3600 * 1000 * 5)

class ReadingTest(TestCase):
  def test_reading(self):
    test_date_string = '2012-01-01T13:00:05'
    test_date = datetime.strptime(test_date_string, '%Y-%m-%dT%H:%M:%S')
    station = Station.objects.create(id='12345', name='test_station')
    reading = Reading.objects.create(
        station=station,
        ip_address='127.0.0.1',
        timestamp=test_date,
        watts=10,
        volts=120,
        amps=1,
        watt_hours=102000,
        power_factor=0,
        frequency=60,
        volt_amps=120,
        relay_status=0,
        power_cycle=0)
    self.assertEquals(unicode(reading), 'test_station::102kWh@' + test_date_string)