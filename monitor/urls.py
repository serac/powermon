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

from django.conf.urls import patterns, include, url
from monitor.views import *

urlpatterns = patterns('',
  url(r'^$', index),
  url(r'^flotseries/([0-9A-Za-z._|]+)/([a-z_|]+)/(\w{2,})/$', flotseries),
  url(r'^leaders/$', leaders),
  url(r'^logout/$', logout),
  url(r'^logout_success/$', logout_success),
  url(r'^record/$', record),
  url(r'^select_station/$', select_station),
  url(r'^status/$', status),
  url(r'^usage/$', usage),
)
