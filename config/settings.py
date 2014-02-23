# This file contains python variables that configure Salmon for email processing.
import logging
import sys
import os

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

receiver_config = {'host': 'localhost', 'port': 8823}

handlers = ['app.server']

router_defaults = {}

