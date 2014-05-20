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

from annoying import fields

try:
    from south.modelsinspector import add_introspection_rules
    SOUTH = True
except ImportError:
    SOUTH = False

class DeferAutoSingleRelatedObjectDescriptor(fields.AutoSingleRelatedObjectDescriptor):
    def __init__(self, defer_fields, related):
        self.defer_fields = defer_fields
        super(DeferAutoSingleRelatedObjectDescriptor, self).__init__(related)

    def get_queryset(self, **db_hints):
        qs = super(DeferAutoSingleRelatedObjectDescriptor, self).get_queryset(**db_hints)
        return qs.defer(*self.defer_fields)

class DeferAutoOneToOneField(fields.AutoOneToOneField):
    def __init__(self, *args, **kwargs):
        self.defer_fields = list(kwargs.pop("defer_fields", []))
        super(DeferAutoOneToOneField, self).__init__(*args, **kwargs)

    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), DeferAutoSingleRelatedObjectDescriptor(self.defer_fields, related))

if SOUTH:
    add_introspection_rules([
        (
            (DeferAutoOneToOneField,),
            [],
            {
                "to": ["rel.to", {}],
                "to_field": ["rel.field_name", {"default_attr": "rel.to._meta.pk.name"}],
                "related_name": ["rel.related_name", {"default": None}],
                "db_index": ["db_index", {"default": True}],
            },
        )
    ],
    ["^inboxen\.fields\.DeferAutoOneToOneField"])
