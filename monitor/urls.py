from django.conf.urls import patterns, include, url
from monitor.views import index, record, select_station, flotseries, usage

urlpatterns = patterns('',
  url(r'^$', index),
  url(r'^record/$', record),
  url(r'^select_station/$', select_station),
  url(r'^flotseries/(\w+)/([a-z_|]+)/(\w{2,})/$', flotseries),
  url(r'^usage/$', usage),
)
