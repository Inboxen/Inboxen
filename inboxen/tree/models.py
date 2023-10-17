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
from django.db.models.base import ModelBase

from inboxen.tree.queryset import NestedSetQuerySet


class TreeBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        new_class = super().__new__(cls, name, bases, attrs, **kwargs)
        cls.get_first_base(new_class)
        return new_class

    def get_first_base(new_class):
        """
        Finds the first concrete super class.

        In the case that multi-table inheritance has been used to allow
        multiple models to be part of the same tree, it is necessary to query
        the whole tree via a common ancestor to be able to access the whole
        tree.

        C: All I'm trying to find out is what's the guy's name on first base?
        A: Oh no no, What is on second.
        C: I'm not asking you who's on second.
        A: Who's on first!
        C: I dunno!
        A: He's on third, we're not talking about him.
        """
        mro_set = set(new_class.__mro__)
        ancestor = NestedSetBase
        while getattr(ancestor._meta, "abstract", False):
            try:
                ancestor = mro_set.intersection(set(ancestor.__subclasses__())).pop()
            except KeyError:
                return

        new_class.tree_base = ancestor


class NestedSetBase(models.Model):
    class Meta:
        abstract = True
        ordering = ["lft"]

    objects = NestedSetQuerySet.as_manager()

    lft = models.PositiveIntegerField(db_index=True)
    rght = models.PositiveIntegerField()
    level = models.PositiveIntegerField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.lft is None:
            # new node
            if self.parent is None:
                # new root node
                self.lft = 1
                self.rght = 2
                self.level = 0
            else:
                last_sibling = self.get_siblings().order_by().last()
                if last_sibling:
                    self.lft = last_sibling.rght + 1
                else:
                    self.lft = self.parent.lft + 1
                self.rght = self.lft + 1
                self.level = self.parent.level + 1

                self.parent.rght = self.rght + 1
                self.parent.save()
        super().save(*args, **kwargs)

    def is_root(self):
        return self.parent_id is None

    def is_leaf_node(self):
        return self.lft == self.rght - 1

    def get_siblings(self):
        if hasattr(self, "_tree_cache") and self.__class__.parent.is_cached(self):
            return [i for i in self.parent.get_children() if i.pk != self.pk]
        else:
            return self.tree_base.objects.filter(
                parent=self.parent_id,
            ).exclude(id=self.id)

    def get_children(self):
        if hasattr(self, "_tree_cache"):
            return self._tree_cache
        else:
            return self.tree_base.objects.filter(
                lft__gt=self.lft,
                rght__lt=self.rght,
                parent=self,
            )


class NestedSet(NestedSetBase, metaclass=TreeBase):
    class Meta:
        abstract = True
