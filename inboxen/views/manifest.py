##
#    Copyright (C) 2018 Jessica Tallon & Matthew Molyneaux
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from django.conf import settings
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_GET


@require_GET
def manifest(request):
    data = {
        "name": settings.SITE_NAME,
        "short_name": settings.SITE_NAME,
        "icons": [
            {
                "src": static("imgs/megmelon-icon-white.png"),
                "sizes": "128x128",
                "type": "image/png"
            }
        ],
        "theme_color": "#ffffff",
        "background_color": "#ffffff",
        "display": "browser",
        "start_url": reverse("user-home"),
    }

    return JsonResponse(data)
