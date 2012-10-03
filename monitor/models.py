from django.db import models


class Station(models.Model):
  """Power monitoring station descriptor"""
  id = models.CharField(primary_key=True, max_length=20)
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=500, null=True, blank=True)
  doc_url = models.CharField('documentation URL', max_length=100, null=True, blank=True)

  def __unicode__(self):
    return self.name


class Reading(models.Model):
  """Power consumption reading provided by a monitoring station"""
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

  def __unicode__(self):
    return '%s::%skWh@%s' % (self.station, self.watt_hours / 1000, self.timestamp.strftime('%Y-%m-%dT%H:%M:%S'))

