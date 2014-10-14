##
#    Copyright (C) 2014 Jessica Tallon & Matt Molyneaux
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
from django.template import loader, Context

from website.context_processors import reduced_settings_context

def generate_maintenance_page():
    """Render maintenance page into static files"""
    template_name = "maintenance.html"
    template = loader.get_template(template_name)
    context = Context(reduced_settings_context(None))
    rendered = template.render(context)

    output_dir = os.path.join(settings.STATIC_ROOT, "pages")
    try:
        os.mkdir(output_dir, 0711)
    except OSError:
        pass

    output_path = os.path.join(output_dir, template_name)

    output = open(output_path, "w")
    output.write(rendered)
    output.close()
