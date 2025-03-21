"""
WSGI config for Employee_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise  # Note the correct case

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Employee_manager.settings')

application = get_wsgi_application()
application = WhiteNoise(application)