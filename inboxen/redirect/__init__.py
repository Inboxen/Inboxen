##
#    Copyright (C) 2015, 2017 Jessica Tallon & Matt Molyneaux
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

from django.urls import reverse
from django.utils.http import urlquote

ALLOW_URL_SCHEMES = [
    'http',
    'https',
]


def proxy_url(url):
    url_parts = url.split(":")
    if len(url_parts) > 1:
        # check to see if the second item is a port number
        try:
            port = int(url_parts[1], 10)
        except ValueError:
            # second part of url was not a port
            port = 0

        # if the second part of a url is not a port, then we can assume the
        # first must be a protocol scheme
        if port == 0 and url_parts[0] not in ALLOW_URL_SCHEMES:
            # url starts with a protocol, but it's not one that we can redirect
            # to safely
            return url

    proxy = reverse("redirect")
    url = urlquote(url)
    return "{proxy}?url={url}".format(proxy=proxy, url=url)
