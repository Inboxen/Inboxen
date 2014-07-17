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

import re

from django.core import exceptions
from django.contrib.contenttypes.models import ContentType
from django.utils import encoding

import watson

HEADER_PARAMS = re.compile(r'([a-zA-Z0-9]+)=["\']?([^"\';=]+)["\']?[;]?')

class EmailSearchAdapter(watson.SearchAdapter):
    trunc_to_size = 2**20 # 1MB. Or two copies of 1984

    # We can't import our models at module load time nor at object
    # initialisation due to circular imports (this class is initialised via
    # inboxen.models), so we'll do it this way instead.
    _model_cache = {}
    def get_model(self, model):
        try:
            model_class = self._model_cache[model]
        except KeyError:
            model_class = ContentType.objects.get(app_label="inboxen", model=model).model_class()
            self._model_cache[model] = model_class
        return model_class

    def get_bodies(self, obj):
        """Return a queryset of text/* bodies for given obj"""
        Body = self.get_model("body")
        data = Body.objects.filter(
                                partlist__email__id=obj.id,
                                partlist__header__name__name="Content-Type",
                                partlist__header__data__data__startswith="text/",
                                )
        if len(data) == 0:
            data = Body.objects.filter(partlist__email__id=obj.id)
            data = data.exclude(partlist__header__name__name="Content-Type")
            data = data.exclude(partlist__header__name__name="MIME-Version")
        return data

    def get_body_charset(self, obj, body):
        """Figure out the charset for the body we've just been given"""
        Header = self.get_model("header")
        content_type = Header.objects.filter(part__email__id=obj.id, part__body__id=body.id, name__name="Content-Type").select_related("data")
        try:
            content_type = content_type[0].data.data
            content_type = content_type.split(";", 1)
            params = dict(HEADER_PARAMS.findall(content_type[1]))
            if "charset" in params:
                encoding = params["charset"]
        except (exceptions.ObjectDoesNotExist, IndexError):
            encoding = "utf-8"

        return encoding

    ## Overridden SearchAdapter methods, see Watson docs

    def get_title(self, obj):
        """Fetch subject for obj"""
        HeaderData = self.get_model("headerdata")
        try:
            subject = HeaderData.objects.filter(
                                header__part__parent__isnull=True,
                                header__name__name="Subject",
                                header__part__email__id=obj.id,
                                )
            subject = subject[0]
            return encoding.smart_text(subject.data, errors='replace')
        except IndexError:
            return u""

    def get_description(self, obj):
        """Fetch first text/* body for obj, reading up to `trunc_to_size` bytes
        """
        try:
            body = self.get_bodies(obj)[0]
        except IndexError:
            return u""

        return encoding.smart_text(body.data[:self.trunc_to_size], encoding=self.get_body_charset(obj, body), errors='replace')

    def get_content(self, obj):
        """Fetch all text/* bodies for obj, reading up to `trunc_to_size` bytes"""
        data = []
        size = 0
        for body in self.get_bodies(obj):
            remains = self.trunc_to_size - size
            size = size + body.size

            if remains <= 0:
                break
            elif remains < body.size:
                data.append(encoding.smart_text(body.data[:remains], encoding=self.get_body_charset(obj, body), errors='replace'))
                break
            else:
                data.append(encoding.smart_text(body.data, encoding=self.get_body_charset(obj, body), errors='replace'))

        return u"\n".join(data)

    def get_meta(self, obj):
        """Extra meta data to save DB queries later"""
        HeaderData = self.get_model("headerdata")
        try:
            from_header = HeaderData.objects.filter(
                                    header__part__parent__isnull=True,
                                    header__name__name="From",
                                    header__part__email__id=obj.id,
                                    )[0]
            from_header = encoding.smart_text(from_header.data, errors='replace')
        except IndexError:
            from_header = u""

        return {
            "from": from_header,
            "inbox": obj.inbox.inbox,
            "domain": obj.inbox.domain.domain,
            }

class InboxSearchAdapter(watson.SearchAdapter):
    def get_title(self, obj):
        return obj.tags or ""

    def get_description(self, obj):
        return u"" # no point in repeating what's in get_title

    def get_content(self, obj):
        return u"" # ditto

    def get_meta(self, obj):
        return {
            "domain": obj.domain.domain,
            }
