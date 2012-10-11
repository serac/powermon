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

from django.db import models


class Station(models.Model):
  """Power monitoring station descriptor."""
  id = models.CharField(primary_key=True, max_length=20)
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=500, null=True, blank=True)
  doc_url = models.CharField('documentation URL', max_length=100, null=True, blank=True)

  def __unicode__(self):
    return self.name


class Reading(models.Model):
  """Power consumption reading provided by a monitoring station."""

  station = models.ForeignKey(Station)
  timestamp = models.DateTimeField(db_index=True)
  ip_address = models.CharField('IP address', max_length=40)
  watts = models.IntegerField()
  volts = models.IntegerField()
  amps = models.IntegerField()
  watt_hours = models.IntegerField('watt hours')
  power_factor = models.IntegerField('power factor')
  frequency = models.IntegerField('frequency')
  volt_amps = models.IntegerField('volt amps')
  relay_status = models.IntegerField('relay status')
  power_cycle = models.IntegerField('power cycle count')

  class Meta:
    permissions = (
        ('data_access', 'Can access power reading data'),
    )

  def __unicode__(self):
    return '%s::%skWh@%s' % (self.station, int(self.watt_hours) / 1000, self.timestamp.strftime('%Y-%m-%dT%H:%M:%S'))

