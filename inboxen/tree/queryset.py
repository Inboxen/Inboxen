##
#    Copyright (C) 2023 Jessica Tallon & Matt Molyneaux
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

from django.db import models


class NestedSetQuerySet(models.query.QuerySet):
    def get_cached_trees(self):
        """
        Cache an entire tree, allowing tree traversal without additional
        database queries. Returns root object rather than a queryset.

        To avoid extra queries use model methods/properties such as `parent`,
        `get_siblings`, and `get_children`.
        """
        root_parts = []
        part_cache = {}

        for part in self.order_by("lft"):
            part_cache[part.id] = part
            setattr(part, "_tree_cache", [])
            try:
                part.parent = part_cache[part.parent_id]
                part.parent._tree_cache.append(part)
            except KeyError:
                root_parts.append(part)

        return root_parts
