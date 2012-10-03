# Powermon: Simple Web-based power consumption data capture and analysis software

Powermon is a simple Django-based Web application for capturing data from a
*watts up? .net* power meter that posts power consumption data to a Web endpoint
for collection.  Powermon also provides a dashboard for monitoring power use
as well as analysis tools to determine and report trends.

## Dependencies

1. Python >2.7
2. Django 1.4
3. NumPy

## Installation/Deployment

Create a settings.py under powermon using settings.py.sample as a template.
The following references are valuable for an Apache+WSGI setup:

* https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
* https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/