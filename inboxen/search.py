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

from inboxen.utils.email import unicode_damnit


def find_body(part):
    if part is not None:
        try:
            main, sub = part.content_type.split("/", 1)
        except ValueError:
            if part.is_leaf_node() and part.get_level() == 0:
                yield part
        else:
            if main == "multipart":
                for child in part.get_children():
                    for grandchild in find_body(child):
                        yield grandchild
            elif main == "text" and sub == "plain":
                yield part


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
        bytes """
        first_part = find_body(obj.get_parts()).next()

        if first_part is not None:
            return unicode_damnit(first_part.body.data[:self.trunc_to_size], first_part.charset)
        else:
            return ""

    def get_content(self, obj):
        """Fetch all text/plain bodies for obj, reading up to `trunc_to_size`
        bytes"""
        data = []
        size = 0
        for part in find_body(obj.get_parts()):
            if part is None:
                break

            remains = self.trunc_to_size - size
            size = size + part.body.size

            if remains <= 0:
                break
            elif remains < part.body.size:
                data.append(unicode_damnit(part.body.data[:remains], part.charset))
                break
            else:
                data.append(unicode_damnit(part.body.data, part.charset))

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
