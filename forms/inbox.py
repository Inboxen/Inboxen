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
from inboxen import models

class InboxAddForm(forms.ModelForm):

	tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Tag1, Tag2, ...'}))

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
		fields = ["domain"]

	def save(self, commit=False):
		# We want this instance created by .create() so we will ignore self.instance
		# which is created just by model(**data)
		data = self.cleaned_data.copy()
		tags = data.pop("tags")
		self.instance = self.request.user.inbox_set.create(**data)
		models.Tag.objects.from_string(tags=tags, inbox=self.instance)
		self.instance.save()
		return self.instance

class InboxEditForm(forms.ModelForm):

	tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Tag1, Tag2, ...'}))

	class Meta:
		model = models.Inbox
		fields = []

	def __init__(self, initial=None, instance=None, *args, **kwargs):
		if not initial:
			initial = {"tags": ", ".join([str(tag) for tag in models.Tag.objects.filter(inbox=instance)])}

		return super(InboxEditForm, self).__init__(instance=instance, initial=initial, *args, **kwargs)

	def save(self, commit=True):
		if not commit:
			return

		self.instance.tag_set.all().delete()
		self.instance.tag_set.from_string(
			tags=self.cleaned_data.get("tags"),
			inbox=self.instance
		)

		return self.instance
