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

from django.db.models import PositiveIntegerField

from inboxen.test import InboxenTestCase
from inboxen.tree import models


class TestTreeModel(models.NestedSet):
    tree_id = PositiveIntegerField(default=1)


class TestMultiTableTreeOneModel(TestTreeModel):
    pass


class TestMultiTableTreeTwoModel(TestMultiTableTreeOneModel):
    pass


class TreeQuerySetTestCase(InboxenTestCase):
    def setUp(self):
        self.root1 = TestTreeModel.objects.create(tree_id=1)
        TestTreeModel.objects.create(parent=self.root1, tree_id=1)
        TestTreeModel.objects.create(parent=self.root1, tree_id=1)

        self.root2 = TestTreeModel.objects.create(tree_id=2)
        root_child1 = TestTreeModel.objects.create(parent=self.root2, tree_id=2)
        TestTreeModel.objects.create(parent=root_child1, tree_id=2)
        TestTreeModel.objects.create(parent=root_child1, tree_id=2)
        root_child2 = TestTreeModel.objects.create(parent=self.root2, tree_id=2)
        TestTreeModel.objects.create(parent=root_child2, tree_id=2)

    def test_cached_trees_single_root(self):
        cached_roots = TestTreeModel.objects.filter(tree_id=2).get_cached_trees()
        self.assertEqual(len(cached_roots), 1)
        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()), 2)
            for child in cached_roots[0].get_children():
                self.assertEqual(child.parent, cached_roots[0])

        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()[0].get_children()), 2)
            for child in cached_roots[0].get_children()[0].get_children():
                self.assertEqual(child.parent, cached_roots[0].get_children()[0])
                self.assertEqual(len(child.get_children()), 0)

        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()[1].get_children()), 1)
            for child in cached_roots[0].get_children()[1].get_children():
                self.assertEqual(child.parent, cached_roots[0].get_children()[1])
                self.assertEqual(len(child.get_children()), 0)

    def test_cached_trees_multiple_roots(self):
        cached_roots = TestTreeModel.objects.all().get_cached_trees()
        cached_roots.sort(key=lambda x: x.tree_id, reverse=True)
        self.assertEqual(len(cached_roots), 2)
        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()), 2)
            for child in cached_roots[0].get_children():
                self.assertEqual(child.parent, cached_roots[0])

        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()[0].get_children()), 2)
            for child in cached_roots[0].get_children()[0].get_children():
                self.assertEqual(child.parent, cached_roots[0].get_children()[0])
                self.assertEqual(len(child.get_children()), 0)

        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[0].get_children()[1].get_children()), 1)
            for child in cached_roots[0].get_children()[1].get_children():
                self.assertEqual(child.parent, cached_roots[0].get_children()[1])
                self.assertEqual(len(child.get_children()), 0)

        with self.assertNumQueries(0):
            self.assertEqual(len(cached_roots[1].get_children()), 2)
            for child in cached_roots[1].get_children():
                self.assertEqual(child.parent, cached_roots[1])
                self.assertEqual(len(child.get_children()), 0)

    def test_cached_trees_subtree(self):
        cached_roots = TestTreeModel.objects.filter(tree_id=2).exclude(parent=None).get_cached_trees()
        with self.assertNumQueries(0):
            for root in cached_roots:
                root.get_children()

        with self.assertNumQueries(2):
            for root in cached_roots:
                self.assertNotEqual(root.parent, None)


class TreeBaseModelTestCase(InboxenTestCase):
    def setUp(self):
        self.root = TestTreeModel.objects.create(tree_id=2)
        self.child1 = TestMultiTableTreeOneModel.objects.create(parent=self.root, tree_id=2)
        self.grandchild1 = TestMultiTableTreeOneModel.objects.create(parent=self.child1, tree_id=2)
        self.grandchild2 = TestMultiTableTreeOneModel.objects.create(parent=self.child1, tree_id=2)
        self.grandchild3 = TestMultiTableTreeTwoModel.objects.create(parent=self.child1, tree_id=2)
        self.child2 = TestMultiTableTreeTwoModel.objects.create(parent=self.root, tree_id=2)
        TestMultiTableTreeOneModel.objects.create(parent=self.child2, tree_id=2)

    def test_tree_base(self):
        self.assertEqual(TestTreeModel.tree_base, TestTreeModel)
        self.assertEqual(TestMultiTableTreeOneModel.tree_base, TestTreeModel)
        self.assertEqual(TestMultiTableTreeTwoModel.tree_base, TestTreeModel)

    def test_get_chilren(self):
        self.assertCountEqual(self.child1.get_children(),
                              [self.grandchild1.testtreemodel_ptr, self.grandchild2.testtreemodel_ptr,
                               self.grandchild3.testtreemodel_ptr])

    def test_get_siblings(self):
        self.assertCountEqual(self.grandchild1.get_siblings(),
                              [self.grandchild2.testtreemodel_ptr, self.grandchild3.testtreemodel_ptr])


class TreeModelTestCase(InboxenTestCase):
    def setUp(self):
        self.root_node = TestTreeModel.objects.create(tree_id=1)
        self.child_node = TestTreeModel.objects.create(tree_id=1, parent=self.root_node)
        self.grandchild_node = TestTreeModel.objects.create(tree_id=1, parent=self.child_node)

    def test_save(self):
        pass

    def test_is_root(self):
        self.assertEqual(self.root_node.is_root(), True)
        self.assertEqual(self.child_node.is_root(), False)
        self.assertEqual(self.grandchild_node.is_root(), False)

    def test_is_leaf_node(self):
        self.assertEqual(self.root_node.is_leaf_node(), False)
        self.assertEqual(self.child_node.is_leaf_node(), False)
        self.assertEqual(self.grandchild_node.is_leaf_node(), True)

    def test_get_siblings(self):
        sibling = TestTreeModel.objects.create(tree_id=1, parent=self.root_node)
        with self.assertNumQueries(1):
            self.assertCountEqual(self.child_node.get_siblings(), [sibling])

    def test_get_siblings_cached(self):
        sibling = TestTreeModel.objects.create(tree_id=1, parent=self.root_node)
        root_node = TestTreeModel.objects.all().get_cached_trees()[0]
        child_node = root_node.get_children()[0]
        with self.assertNumQueries(0):
            self.assertCountEqual(child_node.get_siblings(), [sibling])

    def test_get_chilren(self):
        child = TestTreeModel.objects.create(tree_id=1, parent=self.root_node)
        with self.assertNumQueries(1):
            self.assertCountEqual(self.root_node.get_children(), [self.child_node, child])

    def test_get_chilren_cached(self):
        child = TestTreeModel.objects.create(tree_id=1, parent=self.root_node)
        root_node = TestTreeModel.objects.all().get_cached_trees()[0]
        with self.assertNumQueries(0):
            self.assertCountEqual(root_node.get_children(), [self.child_node, child])
