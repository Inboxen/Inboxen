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

from inboxen.cms import models

PAGE_TYPES = (
    models.HelpIndex,
    models.AppPage,
    models.HelpPage,
    # models.PeoplePage,
)


class DeleteForm(forms.Form):
    yes_delete = forms.BooleanField()


class HelpBasePageForm(forms.ModelForm):
    model_ct = None  # populated by get_page_form

    def clean(self):
        cleaned_data = super(HelpBasePageForm, self).clean()
        if "slug" not in self.errors:  # "slug" won't be in cleaned_data if there was an error
            slug = cleaned_data["slug"]
            parent = self.instance.parent
            if parent:
                siblings = parent.get_children()
                if self.instance.pk:
                    siblings = siblings.exclude(pk=self.instance.pk)

                if siblings.filter(slug=slug).exists():
                    raise forms.ValidationError({'slug': "Must be unique within siblings"})

        return cleaned_data


def get_page_form(model_ct, form=HelpBasePageForm):
    model = model_ct.model_class()
    assert issubclass(model, models.HelpBasePage) and model != models.HelpBasePage, \
        "Model must be a subclass of HelpBasePage, but not HelpBasePage itself."
    assert model in PAGE_TYPES, "Not a supported model"

    form = forms.modelform_factory(model, form=form, fields=model.admin_fields)
    form.model_ct = model_ct

    return form
