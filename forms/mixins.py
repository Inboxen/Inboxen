##
#    Copyright (C) 2013-2014 Jessica Tallon & Matt Molyneaux
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

from django.forms import forms, widgets

class BoundField(forms.BoundField):
    """A Field plus data

    And a SR-only label"""
    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        if attrs is None:
            attrs = {}
        attrs["class"] = "sr-only"
        return super(BoundField, self).label_tag(contents, attrs, label_suffix)

class SROnlyLabelMixin(object):
    """Mark field labels as sr-only"""
    def __getitem__(self, name):
        "Returns our BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return BoundField(self, field, name)

class BootstrapFormMixin(object):
    """Mixin for add CSS classes to Django forms

    Needs self.fields to be initialised first
    """
    def __init__(self, *args, **kwargs):
        output = super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, widgets.CheckboxInput):
                field.widget.attrs.update({"class": "form-control"})
        return output

class PlaceHolderMixin(object):
    """Grabs the label of a text widget and adds it as the placeholder value"""
    def __init__(self, *args, **kwargs):
        output = super(PlaceHolderMixin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            label = field.label.title()
            field.widget.attrs.update({"placeholder": label})
        return output
