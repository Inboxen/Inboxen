##
#    Copyright (C) 2017 Jessica Tallon & Matt Molyneaux
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

from blog.models import BlogPost


class CreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(CreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CreateForm, self).save(commit=False)
        instance.author = self.user

        if commit:
            instance.save()

        return instance

    class Meta:
        model = BlogPost
        fields = ["subject", "body"]


class EditForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["subject", "body", "draft"]
