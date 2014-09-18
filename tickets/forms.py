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
from django.utils.translation import ugettext_lazy as _

from tickets import models
from website.forms import mixins

class QuestionForm(mixins.BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ["subject", "body"]
        labels = {"body": _("Question")}

class ResponseForm(mixins.BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = models.Response
        fields = ["body"]
        labels = {"body": _("Reply")}

class QuestionStatusUpdateForm(mixins.BootstrapFormMixin, forms.Form):
    status = forms.ChoiceField(required=True, choices=models.Question.STATUS_CHOICES)

    def __init__(self, question, *args, **kwargs):
        self.question = question
        return super(QuestionStatusUpdateForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        cleaned_data = super(QuestionStatusUpdateForm, self).clean(*args, **kwargs)
        self.question.status = cleaned_data["status"]

        return cleaned_data

    def save(self):
        self.question.save()
