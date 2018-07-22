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

import pprint
import sys

from django.urls import resolve, Resolver404
from django.core.management.base import BaseCommand

_help = """
Given a list of URLs, will display statistics for named URLs.

Single argument is either a file path or '-' for stdin.

To use with your HTTPd logs, use the "awk" command to pull the URLs out. For
example, given a log file where the URL is the third item on a line:

    awk '{print $3}' /path/to/access.log | python manage.py url_stats -
"""


class Command(BaseCommand):
    help = _help

    def add_arguments(self, parser):
        parser.add_argument("file", help="file or '-' for stdin")

    def handle(self, **options):
        pp = pprint.PrettyPrinter(indent=5)

        if options["file"].strip() == "-":
            file_obj = sys.stdin
        else:
            file_obj = open(options["file"], "r")

        urls, non_match = self.count_urls(file_obj)

        self.stdout.write("URLs:\n")
        pp.pprint(urls)

        self.stdout.write("\nNon-matches:\n")
        pp.pprint(non_match)

    def count_urls(self, file_obj):
        urls = {}
        non_match = set()
        for url in file_obj:
            url = url.strip()
            try:
                name = resolve(url).url_name
            except Resolver404:
                non_match.add(url)
                continue

            if name in urls:
                urls[name] = urls[name] + 1
            else:
                urls[name] = 1

        return urls, non_match
