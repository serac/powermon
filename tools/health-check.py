#!/usr/bin/python

# Health check script that examines the /status/ URI and sends mail on any
# condition other than 200/OK.
# Configuration is via environment variables:
#  * POWERMON_STATUS   - absolute URL to /status/ URI
#  * POWERMON_SMTPHOST - SMTP host name used to send mail
#  * POWERMON_MAILTO   - email address where problem reports are sent

from email.mime.text import MIMEText
from httplib import HTTPConnection, HTTPSConnection
from os import environ
from os.path import basename
from smtplib import SMTP
from urlparse import urlparse
import sys


def getenvars(*vars):
  """Returns the values of one or more environment variables."""
  values = []
  for var in vars:
    if not var in environ:
      die('%s environment variable not defined' % var)
    values.append(environ[var])
  return tuple(values)


def die_err(e, message):
  """Displays exception details and a message then exits program."""
  print message
  print e
  sys.exit(1)


def die(message):  
  """Displays a message then exits program."""
  print message
  sys.exit(1)


def http_get(url):
  """Returns the tuple (status, response body) for a GET request to the given URL."""
  conn = None
  headers = {
    'Accept': 'text/plain, text/html, text/xml',
    'Content-Length': 0,
    'User-Agent': 'Python/%s.%s.%s' % sys.version_info[0:3]
  }
  result = urlparse(url)
  try :
    if result.scheme == 'https':
      conn = HTTPSConnection(result.netloc)
    else:
      conn = HTTPConnection(result.netloc)
    conn.request('GET', url, "", headers)
    response = conn.getresponse()
    return (response.status, str(response.read()))
  except Exception, e:
    die_err(e, 'HTTP GET failed:')
  finally:
    if conn: conn.close()


def send_mail(mfrom, mto, body, smtp_host):
  """Sends a health check failure notice to the designated recipient."""
  msg = MIMEText(body)
  msg['Subject'] = 'Powermon Health Check Failure'
  msg['From'] = mfrom
  msg['To'] = mto
  s = SMTP(smtp_host)
  try:
    s.sendmail(mfrom, [mto], msg.as_string())
  finally:
    s.quit


(status_url, mailto, smtp_host) = getenvars(
  'POWERMON_STATUS', 'POWERMON_MAILTO', 'POWERMON_SMTPHOST')

hostname = 'localhost'
if 'HOSTNAME' in environ:
  hostname = environ['HOSTNAME']
mailfrom = '%s@%s' % (environ['USER'], hostname)

print 'Checking', status_url
(status, body) = http_get(status_url)
print body
if status > 200:
  print 'Sending failure notice to', mailto
  send_mail(mailfrom, mailto, body, smtp_host)
