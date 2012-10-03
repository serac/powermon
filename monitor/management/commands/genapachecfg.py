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
