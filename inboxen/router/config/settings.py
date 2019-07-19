import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inboxen.settings')

django.setup()
