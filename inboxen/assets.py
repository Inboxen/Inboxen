##
#    Copyright (C) 2015-2016, 2018 Jessica Tallon & Matt Molyneaux
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


thirdparty_path = os.path.join(os.getcwd(), "node_modules")
sass = get_filter("scss", style="compressed", load_paths=("./css", thirdparty_path))


uglify_args = ["--comments", "/^!/", "-m", "-c"]
uglify = get_filter("uglifyjs", binary=os.path.join(thirdparty_path, ".bin", "uglifyjs"), extra_args=uglify_args)


css = Bundle(
    "css/inboxen.scss",
    filters=(sass,),
    output="compiled/css/website.%(version)s.css",
)
register("inboxen_css", css)


js = Bundle(
    "thirdparty/jquery/dist/jquery.js",
    "js/utils.js",
    "js/copy.js",
    "js/alert.js",
    "js/home.js",
    "js/search.js",
    "js/inbox.js",
    filters=(uglify,),
    output="compiled/js/website.%(version)s.js",
)
register("inboxen_js", js)


chart_js = Bundle(
    "thirdparty/chart.js/dist/Chart.js",
    "js/stats.js",
    filters=(uglify,),
    output="compiled/js/stats.%(version)s.js",
)
register("chart_js", chart_js)
