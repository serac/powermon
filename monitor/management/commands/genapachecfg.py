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

from powermon.settings import APPLICATION_ROOT, STATIC_ROOT, WSGI_ROOT
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.template import Context

class Command(BaseCommand):
  def handle(self, *args, **options):
    template = get_template('apache-wsgi.conf.tmpl')
    context = Context()
    context['APPLICATION_ROOT'] = APPLICATION_ROOT
    context['STATIC_ROOT'] = STATIC_ROOT
    context['WSGI_ROOT'] = WSGI_ROOT
    print template.render(context)
