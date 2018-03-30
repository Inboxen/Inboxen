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

import random

from django import forms
from django.contrib import messages
from django.db.models import F
from django.utils.translation import ugettext as _

from inboxen import models, tasks

__all__ = ["InboxAddForm", "InboxEditForm"]


class InboxAddForm(forms.ModelForm):
    exclude_from_unified = forms.BooleanField(required=False, label=_("Exclude from Unified Inbox"))

    def __init__(self, request, initial=None, *args, **kwargs):
        self.request = request  # needed to create the inbox

        domain_qs = models.Domain.objects.available(self.request.user)

        if not initial:
            initial = {
                "inbox": None,  # This is filled in by the manager.create
            }
            prefered_domain = self.request.user.inboxenprofile.prefered_domain
            if prefered_domain is not None and prefered_domain in domain_qs:
                initial["domain"] = prefered_domain
            else:
                initial["domain"] = random.choice(domain_qs)

        super(InboxAddForm, self).__init__(initial=initial, *args, **kwargs)
        self.fields["domain"].empty_label = None
        self.fields["domain"].queryset = domain_qs

    class Meta:
        model = models.Inbox
        fields = ["domain", "description"]

    def clean(self):
        if self.request.user.inboxenprofile.available_inboxes() <= 0:
            raise forms.ValidationError(_("You have too many Inboxes."))

    def save(self):
        # We want this instance created by .create() so we will ignore self.instance
        # which is created just by model(**data)
        data = self.cleaned_data.copy()
        description = data.pop("description")
        excludes = data.pop("exclude_from_unified", False)

        self.instance = self.request.user.inbox_set.create(**data)
        self.instance.description = description
        self.instance.flags.exclude_from_unified = excludes
        self.instance.save()

        msg = _("{0}@{1} has been created.").format(self.instance.inbox, self.instance.domain.domain)
        messages.success(self.request, msg)
        return self.instance


class InboxSecondaryEditForm(forms.Form):
    """A subform to hold dangerous operations that will result in loss
    of data.
    """
    clear_inbox = forms.BooleanField(required=False, label=_("Empty Inbox"),
                                     help_text=_("Delete all emails in this Inbox. Cannot be undone."))
    disable_inbox = forms.BooleanField(required=False, label=_("Disable Inbox"),
                                       help_text=_("This Inbox will no longer receive emails."))

    def __init__(self, instance, *args, **kwargs):
        super(InboxSecondaryEditForm, self).__init__(*args, **kwargs)
        self.fields["disable_inbox"].initial = bool(instance.flags.disabled)


class InboxEditForm(forms.ModelForm):
    exclude_from_unified = forms.BooleanField(required=False, label=_("Exclude from Unified Inbox"))
    pinned = forms.BooleanField(required=False, label=_("Pin Inbox to top"))

    class Meta:
        model = models.Inbox
        fields = ["description"]

    def __init__(self, request, initial=None, instance=None, *args, **kwargs):
        self.request = request
        super(InboxEditForm, self).__init__(instance=instance, initial=initial, *args, **kwargs)
        self.fields["exclude_from_unified"].initial = bool(self.instance.flags.exclude_from_unified)
        self.fields["pinned"].initial = bool(self.instance.flags.pinned)
        self.subform = InboxSecondaryEditForm(instance=self.instance, **kwargs)

    def clean(self):
        if self.subform.is_valid():
            self.cleaned_data.update(self.subform.cleaned_data)

        disabled = self.cleaned_data.get("disable_inbox", False)
        pinned = self.cleaned_data.get("pinned", False)

        if disabled and pinned:
            raise forms.ValidationError(_("Inbox cannot be disabled and pinned at the same time"))

    def save(self):
        data = self.cleaned_data.copy()
        self.instance.flags.exclude_from_unified = data.pop("exclude_from_unified", False)
        self.instance.flags.pinned = data.pop("pinned", False)
        self.instance.flags.disabled = data.pop("disable_inbox", False)
        clear_inbox = data.pop("clear_inbox", False)

        if clear_inbox:
            emails = self.instance.email_set.all()
            emails.update(flags=F('flags').bitor(models.Email.flags.deleted))
            tasks.batch_delete_items.delay("email", kwargs={'inbox__id': self.instance.id})
            warn_msg = _("All emails in {0}@{1} are being deleted.").format(self.instance.inbox,
                                                                            self.instance.domain.domain)
            messages.warning(self.request, warn_msg)

        self.instance.save()

        return self.instance
