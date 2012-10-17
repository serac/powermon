# Powermon:
# Web-based power consumption data capture and analysis

Powermon is a simple Django-based Web application for capturing data from a
*watts up? .net* power meter that posts power consumption data to a Web endpoint
for collection.  Powermon also provides a dashboard for monitoring power use
as well as analysis tools to determine and report trends.

## Dependencies

1. Python >=2.7
2. Django 1.4
3. NumPy

## Installation/Deployment

1. Extract the source into a location such as /var/www/powermon. This is the
application root path, APPLICATION_ROOT.

2. Create a settings.py in APPLICATION_ROOT/powermon using settings.py.sample
as a template.

3. Install any necessary database integration components for your database
platform such as mysql-python or psycopg2.

4. Provision and initialize database with following command executed from
within APPLICATION_ROOT:

    python manage.py syncdb

  Be sure to create an admin user when prompted if using the Django admin
application (strongly recommended).

5. Integrate the application with a Web server using, for example, the WSGI
framework. The following references are valuable for an Apache+WSGI setup:
  * https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
  * https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/modwsgi/

  Additionally, the following command may be helpful for generating an Apache
mod_wsgi configuration:

    python manage.py genapachecfg

6. Make application static content available to Web server using the following
command:

    python manage.py collectstatic
