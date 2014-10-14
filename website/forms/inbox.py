##
#    Copyright (C) 2013 Jessica Tallon & Matt Molyneaux
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

from datetime import datetime
import random

from django.utils.translation import ugettext as _
from django import forms
from django.contrib import messages

from pytz import utc
import watson

from inboxen import models
from queue.delete import tasks

__all__ = ["InboxAddForm", "InboxEditForm", "InboxRestoreForm"]

class InboxAddForm(forms.ModelForm):
    exclude_from_unified = forms.BooleanField(required=False, label=_("Exclude from Unified Inbox"))

    def __init__(self, request, initial=None, *args, **kwargs):
        self.request = request # needed to create the inbox

        if not initial:
            initial = {
                "inbox": None, # This is filled in by the manager.create
                "domain": random.choice(models.Domain.objects.all()),
            }

        super(InboxAddForm, self).__init__(initial=initial, *args, **kwargs)
        # Remove empty option "-------"
        self.fields["domain"].empty_label = None

    class Meta:
        model = models.Inbox
        fields = ["domain", "tags"]
        widgets = {
            "tags": forms.TextInput(attrs={'placeholder': 'Tag1, Tag2, ...'})
            }

    def save(self, commit=True):
        # We're ignoring commit, should we?
        # We want this instance created by .create() so we will ignore self.instance
        # which is created just by model(**data)
        data = self.cleaned_data.copy()
        tags = data.pop("tags")
        excludes = data.pop("exclude_from_unified", False)

        self.instance = self.request.user.inbox_set.create(**data)
        self.instance.tags = tags
        self.instance.flags.exclude_from_unified = excludes
        self.instance.save()

        messages.success(self.request, _("{0}@{1} has been created.").format(self.instance.inbox, self.instance.domain.domain))
        return self.instance

class InboxSecondaryEditForm(forms.Form):
    """A subform to hold dangerous operations that will result in loss
    of data.
    """
    clear_inbox = forms.BooleanField(required=False, label=_("Clear Inbox"), help_text=_("Delete all emails in this Inbox. Cannot be undone."))
    disable_inbox = forms.BooleanField(required=False, label=_("Disable Inbox"), help_text=_("This Inbox will no longer receive emails."))

    def __init__(self, instance, *args, **kwargs):
        super(InboxSecondaryEditForm, self).__init__(*args, **kwargs)
        self.fields["disable_inbox"].initial = bool(instance.flags.disabled)

class InboxEditForm(forms.ModelForm):
    exclude_from_unified = forms.BooleanField(required=False, label=_("Exclude from Unified Inbox"))

    class Meta:
        model = models.Inbox
        fields = ["tags"]
        widgets = {
            "tags": forms.TextInput(attrs={'placeholder': 'Tag1, Tag2, ...'})
            }

    def __init__(self, request, initial=None, instance=None, *args, **kwargs):
        self.request = request
        super(InboxEditForm, self).__init__(instance=instance, initial=initial, *args, **kwargs)
        self.fields["exclude_from_unified"].initial = bool(self.instance.flags.exclude_from_unified)
        self.subform = InboxSecondaryEditForm(instance=self.instance, **kwargs)

    def save(self, commit=True):
        data = self.cleaned_data.copy()
        if self.subform.is_valid():
            data.update(self.subform.cleaned_data.copy())

        self.instance.flags.exclude_from_unified = data.pop("exclude_from_unified", False)
        self.instance.flags.disabled = data.pop("disable_inbox", False)
        clear_inbox = data.pop("clear_inbox", False)

        if not commit:
            return self.instance

        if clear_inbox:
            tasks.batch_delete_items.delay("email", kwargs={'inbox__id': self.instance.id})
            messages.warning(self.request, _("All emails in {0}@{1} are being deleted.").format(self.instance.inbox, self.instance.domain.domain))

        self.instance.save()

        return self.instance

class InboxRestoreForm(InboxEditForm):
    def save(self, commit=True):
        self.instance.flags.deleted = False
        self.instance.created = datetime.now(utc)
        return super(InboxRestoreForm, self).save(commit)
