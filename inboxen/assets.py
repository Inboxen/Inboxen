##
#    Copyright (C) 2015 Jessica Tallon & Matt Molyneaux
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
#    along with Inboxen.  If not, see <http://www.gnu.org/licenses/>.
##

import os

from django.conf import settings

from django_assets import Bundle, register
from webassets.filter import get_filter

thirdparty_path = os.path.join(settings.BASE_DIR, "node_modules")
sass = get_filter('scss', style="compressed", load_paths=(thirdparty_path,))


css = Bundle(
    "css/inboxen.scss",
    filters=(sass,),
    output="compiled/css/website.%(version)s.css",
)


js = Bundle(
    "thirdparty/jquery/dist/jquery.js",
    "thirdparty/bootstrap-sass/assets/javascripts/bootstrap.js",
    "js/menu.js",
    "js/home.js",
    "js/search.js",
    "js/inbox.js",
    "js/email.js",  # make sure this one is last
    filters="jsmin",
    output="compiled/js/website.%(version)s.js",
)

register("inboxen_css", css)
register("inboxen_js", js)
