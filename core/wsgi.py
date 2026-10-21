"""
WSGI config for core project on Vercel and production servers.

It exposes the WSGI callable as a module-level variable named ``application``
and ``app`` (required by Vercel serverless runtime).

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Vercel Serverless Function entrypoint
app = application
