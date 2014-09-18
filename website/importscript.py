##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
#   
#    This file is part of Inboxen.
#
#    Inboxen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Inboxen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Inboxen  If not, see <http://www.gnu.org/licenses/>.
##

"""
This file is for use with mod_wsgi's WSGIImportScript directive.

It undoes a lot of the lazy-loading that Django will normally do and makes the
first request after a reload (whether that be via Apache or `touch`ing wsgi.py)
much less painful for end-users.
"""

import sys
import os

import djcelery
djcelery.setup_loader()

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "inboxen.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# force loading of various parts, lazy loading be damned
from django.core.urlresolvers import reverse
from django.conf import settings

settings.DEBUG
reverse("index")

