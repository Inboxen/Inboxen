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

from django import forms
from django.utils.translation import gettext_lazy as _

from inboxen.tickets import models


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ["subject", "body"]
        labels = {"body": _("Question")}


class ResponseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop("question")
        self.author = kwargs.pop("author")
        super(ResponseForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ResponseForm, self).save(commit=False)
        instance.author = self.author
        instance.question = self.question
        if commit:
            instance.save()

        return instance

    class Meta:
        model = models.Response
        fields = ["body"]
        labels = {"body": _("Reply")}


class ResponseAdminForm(ResponseForm):
    status = forms.ChoiceField(choices=models.Question.STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop("initial", {})
        initial["status"] = kwargs["question"].status
        kwargs["initial"] = initial

        super(ResponseAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ResponseAdminForm, self).save(commit=False)
        self.question.status = self.cleaned_data["status"]

        if commit:
            instance.save()
            self.question.save()

        return instance

    class Meta:
        model = models.Response
        fields = ["body"]
        labels = {"body": _("Reply")}
