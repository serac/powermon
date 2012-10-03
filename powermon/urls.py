from django.conf.urls import patterns, include, url
from django.contrib import admin
from powermon.settings import ROOT_URL

admin.autodiscover()

urlpatterns = patterns('',
  url('^' + ROOT_URL[1:], include('monitor.urls')),
  url(r'^admin/', include(admin.site.urls)),
)
