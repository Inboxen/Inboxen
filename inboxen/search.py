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

from django.contrib.contenttypes.models import ContentType
from django.utils import encoding

import watson

class EmailSearchAdapter(watson.SearchAdapter):
    trunc_to_size = 2**20 # 1MB. Or two copies of 1984

    def get_title(self, obj):
        HeaderData = ContentType.objects.get(app_label="inboxen", model="headerdata").model_class()
        try:
            subject = HeaderData.objects.filter(
                                header__part__parent__isnull=True,
                                header__name__name="Subject",
                                header__part__email__id=obj.id,
                                )
            subject = subject[0]
            return encoding.smart_text(subject.data)
        except IndexError:
            return u""

    def get_bodies(self, obj):
        Body = ContentType.objects.get(app_label="inboxen", model="body").model_class()
        data = Body.objects.filter(
                                partlist__email__id=obj.id,
                                partlist__header__name__name="Content-Type",
                                partlist__header__data__data__startswith="text/",
                                )
        return data

    def get_description(self, obj):
        try:
            body = self.get_bodies(obj)[0]
            return encoding.smart_text(body.data[:self.trunc_to_size])
        except IndexError:
            return u""

    def get_content(self, obj):
        data = []
        size = 0
        for body in self.get_bodies(obj):
            remains = self.trunc_to_size - size
            size = size + body.size

            if remains <= 0:
                break
            elif remains < body.size:
                data.append(encoding.smart_text(body.data[:remains]))
                break
            else:
                data.append(encoding.smart_text(body.data))

        return u"\n".join(data)

    def get_meta(self, obj):
        HeaderData = ContentType.objects.get(app_label="inboxen", model="headerdata").model_class()
        try:
            from_header = HeaderData.objects.filter(
                                    header__part__parent__isnull=True,
                                    header__name__name="From",
                                    header__part__email__id=obj.id,
                                    )[0]
            from_header = encoding.smart_text(from_header.data)
        except IndexError:
            from_header = u""

        return {
            "from": from_header,
            "inbox": obj.inbox.inbox,
            "domain": obj.inbox.domain.domain,
            }

class InboxSearchAdapter(watson.SearchAdapter):
    def get_title(self, obj):
        return ", ".join([tag.tag for tag in obj.tag_set.only("tag").iterator()])

    def get_description(self, obj):
        return u""

    def get_content(self, obj):
        return u""

    def get_meta(self, obj):
        return {
            "domain": obj.domain.domain,
            }
