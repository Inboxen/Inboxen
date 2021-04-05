##
#    Copyright (C) 2013-2015 Jessica Tallon & Matt Molyneaux
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

from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _

from inboxen import models
from inboxen.liberation.tasks import liberate as data_liberate


class LiberationForm(forms.ModelForm):
    class Meta:
        model = models.Inbox
        fields = []

    STORAGE_TYPES = (
        (0, _("Maildir")),
        (1, _("Mailbox .mbox")),
    )

    # Could we support zip files?
    COMPRESSION_TYPES = (
        (0, _("Tarball (gzip compressed)")),
        (1, _("Tarball (bzip2 compression)")),
        (2, _("Tarball (no compression)")),
    )

    storage_type = forms.ChoiceField(choices=STORAGE_TYPES)
    compression_type = forms.ChoiceField(choices=COMPRESSION_TYPES)

    def __init__(self, user, initial=None, *args, **kwargs):
        self.user = user
        if not initial:
            initial = {
                "storage_type": 0,
                "compression_type": 0,
            }

        return super(LiberationForm, self).__init__(initial=initial, *args, **kwargs)

    def save(self):
        lib_status = self.user.liberation
        if not lib_status.running:
            lib_status.running = True
            lib_status.started = timezone.now()

            result = data_liberate.apply_async(
                kwargs={"user_id": self.user.id, "options": self.cleaned_data},
                countdown=10
            )

            lib_status.async_result = result.id
            lib_status.save()

        return self.user
