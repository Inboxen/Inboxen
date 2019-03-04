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

from watson import search

from inboxen.utils.email import unicode_damnit


class EmailSearchAdapter(search.SearchAdapter):
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
        """"""
        from inboxen.models import HeaderData

        try:
            from_header = HeaderData.objects.filter(
                header__part__parent__isnull=True,
                header__name__name="From",
                header__part__email__id=obj.id,
            ).first()

            return unicode_damnit(from_header.data)
        except AttributeError:
            return u""

    def get_content(self, obj):
        return u""  # nothing else is needed for search

    def get_meta(self, obj):
        """Extra meta data to save DB queries later"""
        return {
            "inbox": obj.inbox.inbox,
            "domain": obj.inbox.domain.domain,
        }


class InboxSearchAdapter(search.SearchAdapter):
    def get_title(self, obj):
        return obj.description or u""

    def get_description(self, obj):
        return str(obj)

    def get_content(self, obj):
        return u""  # nothing else is needed for search

    def get_meta(self, obj):
        """Extra meta data to save DB queries later"""
        return {
            "domain": obj.domain.domain,
        }
