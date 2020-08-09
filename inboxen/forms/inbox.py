##
#    Copyright (C) 2013, 2018 Jessica Tallon & Matt Molyneaux
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

from celery import chain
from django import forms
from django.contrib import messages
from django.utils.translation import ugettext as _

from inboxen import models, tasks
from inboxen.account.tasks import disown_inbox
from inboxen.utils.ratelimit import inbox_ratelimit


class InboxAddForm(forms.ModelForm):
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
        fields = ["domain", "description", "exclude_from_unified"]

    def clean(self):
        if inbox_ratelimit.counter_full(self.request):
            raise forms.ValidationError(_("Slow down! You're creating inboxes too quickly."))

    def save(self):
        # We want this instance created by .create() so we will ignore self.instance
        # which is created just by model(**data)
        data = self.cleaned_data.copy()

        self.instance = self.request.user.inbox_set.create(**data)
        self.instance.update_search()
        self.instance.save()
        inbox_ratelimit.counter_increase(self.request)

        msg = _("{0}@{1} has been created.").format(self.instance.inbox, self.instance.domain.domain)
        messages.success(self.request, msg)
        return self.instance


class InboxEditForm(forms.ModelForm):
    clear_inbox = forms.BooleanField(required=False, label=_("Empty Inbox"),
                                     help_text=_("Delete all emails in this Inbox. Cannot be undone."))

    class Meta:
        model = models.Inbox
        fields = ["description", "exclude_from_unified", "pinned", "disabled"]

    def __init__(self, request, initial=None, instance=None, *args, **kwargs):
        self.request = request
        super(InboxEditForm, self).__init__(instance=instance, initial=initial, *args, **kwargs)

    def clean(self):
        disabled = self.cleaned_data.get("disable_inbox", False)
        pinned = self.cleaned_data.get("pinned", False)

        if disabled and pinned:
            raise forms.ValidationError(_("Inbox cannot be disabled and pinned at the same time"))

    def save(self):
        data = self.cleaned_data
        clear_inbox = data.pop("clear_inbox", False)

        if clear_inbox:
            tasks.batch_mark_as_deleted("email", kwargs={"inbox_id": self.instance.id})
            chain(
                tasks.inbox_new_flag.si(self.instance.user_id, self.instance.id),
                tasks.inbox_new_flag.si(self.instance.user_id),
                tasks.batch_delete_items.si("email", kwargs={'inbox_id': self.instance.id, "deleted": True}),
            ).apply_async()
            warn_msg = _("All emails in {0}@{1} are being deleted.").format(self.instance.inbox,
                                                                            self.instance.domain.domain)
            messages.warning(self.request, warn_msg)

        super(InboxEditForm, self).save(commit=False)
        self.instance.update_search()
        self.instance.save()

        return self.instance


class InboxDisownForm(forms.ModelForm):
    disown = forms.BooleanField(
        required=True, label=_("Yes, I'm sure!"),
        help_text=_("Delete this Inbox. No one will be able to use it again and there is no undo button!"),
    )

    class Meta:
        model = models.Inbox
        fields = []

    def __init__(self, request, initial=None, instance=None, *args, **kwargs):
        self.request = request
        super().__init__(instance=instance, initial=initial, *args, **kwargs)

    def save(self):
        self.instance.deleted = True
        warn_msg = _("{0}@{1} has been deleted.").format(self.instance.inbox,
                                                         self.instance.domain.domain)
        messages.warning(self.request, warn_msg)

        super().save()

        disown_inbox.delay(self.instance.id)

        return self.instance
