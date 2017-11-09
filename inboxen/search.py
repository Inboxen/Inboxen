##
#    Copyright (C) 2014-2015 Jessica Tallon & Matt Molyneaux
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

from django.core import exceptions
from django.db.models import Q

from watson import search

from inboxen.utils.email import unicode_damnit, find_bodies

def choose_body(parts):
    """Given a list of sibling MIME parts, choose the one with a content_type
    of "text/plain", if it exists"""
    if len(parts) == 1:
        return unicode_damnit(parts[0].body.data, parts[0].charset)
    elif len(parts) > 1:
        data = u""
        for p in parts:
            if p.content_type == "text/plain":
                data = unicode_damnit(p.body.data, p.charset)
                break
        return data
    else:
        return u""


class EmailSearchAdapter(search.SearchAdapter):
    trunc_to_size = 2 ** 20  # 1MB. Or two copies of 1984

    def get_title(self, obj):
        """Fetch subject for obj"""
        from inboxen.models import HeaderData

        try:
            subject = HeaderData.objects.filter(
                header__part__parent__isnull=True,
                header__name__name="Subject",
                header__part__email__id=obj.id,
            ).first()

            return unicode_damnit(subject.data)
        except AttributeError:
            return u""

    def get_description(self, obj):
        """Fetch first text/plain body for obj, reading up to `trunc_to_size`
        bytes
        """
        bodies = find_bodies(obj.get_parts()).next()

        if bodies is not None:
            return choose_body(bodies)[:self.trunc_to_size]
        else:
            return u""

    def get_content(self, obj):
        """Fetch all text/plain bodies for obj, reading up to `trunc_to_size`
        bytes and excluding those that would not be displayed
        """
        data = []
        size = 0
        for parts in find_bodies(obj.get_parts()):
            remains = self.trunc_to_size - size

            if remains <= 0:
                break

            body = choose_body(parts)[:remains]
            size += len(body)
            data.append(body)

        return u"\n".join(data)

    def get_meta(self, obj):
        """Extra meta data to save DB queries later"""
        from inboxen.models import HeaderData

        try:
            from_header = HeaderData.objects.filter(
                header__part__parent__isnull=True,
                header__name__name="From",
                header__part__email__id=obj.id,
            )[0]
            from_header = unicode_damnit(from_header.data)
        except IndexError:
            from_header = u""

        return {
            "from": from_header,
            "inbox": obj.inbox.inbox,
            "domain": obj.inbox.domain.domain,
        }


class InboxSearchAdapter(search.SearchAdapter):
    def get_title(self, obj):
        return obj.description or ""

    def get_description(self, obj):
        return u""  # no point in repeating what's in get_title

    def get_content(self, obj):
        return u""  # ditto

    def get_meta(self, obj):
        return {
            "domain": obj.domain.domain,
        }
