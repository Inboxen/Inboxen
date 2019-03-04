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

from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError

from inboxen.cms import models, forms
from inboxen.test import InboxenTestCase


class DeleteFormTestCase(InboxenTestCase):
    def test_form_invalid(self):
        form = forms.DeleteForm(data={"yes_delete": False})
        self.assertFalse(form.is_valid())

        form = forms.DeleteForm(data={})
        self.assertFalse(form.is_valid())

    def test_form_valid(self):
        form = forms.DeleteForm(data={"yes_delete": True})
        self.assertTrue(form.is_valid())


class HelpBasePageForm(InboxenTestCase):
    def setUp(self):
        model_ct = ContentType.objects.get_for_model(models.HelpBasePage)

        class TestForm(forms.HelpBasePageForm):
            class Meta:
                model = models.HelpBasePage
                fields = ["slug"]

        TestForm.model_ct = model_ct

        self.TestForm = TestForm

    def test_form_properties(self):
        self.assertEqual(forms.HelpBasePageForm.model_ct, None)

    def test_clean(self):
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()
        form = self.TestForm(instance=page)
        form.cleaned_data = {"slug": "test"}

        self.assertEqual(form.clean(), form.cleaned_data)

    def test_clean_ignores_self(self):
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()
        form = self.TestForm(instance=page)
        form.cleaned_data = {"slug": page.slug}

        self.assertEqual(form.clean(), form.cleaned_data)

    def test_clean_checks_siblings(self):
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()
        form = self.TestForm(instance=page)
        form.cleaned_data = {"slug": "test"}
        new_page = models.HelpBasePage.objects.create(parent=page.parent, content_type=page.content_type, slug="test")

        with self.assertRaises(ValidationError):
            form.clean()

        new_page.delete()

        # doesn't check against parent
        form.cleaned_data["slug"] = page.parent.slug
        self.assertEqual(form.clean(), form.cleaned_data)

    def test_null(self):
        class TestForm(forms.HelpBasePageForm):
            class Meta:
                model = models.HelpBasePage
                fields = ["title", "description", "slug"]

        TestForm.model_ct = self.TestForm.model_ct
        page = models.HelpBasePage.objects.filter(parent__isnull=False).get()

        # clean
        form = TestForm(instance=page, data={"title": "title", "description": "desc", "slug": "slug"})
        self.assertTrue(form.is_valid())

        # title
        form = TestForm(instance=page, data={"title": "title\x00", "description": "desc", "slug": "slug"})
        self.assertFalse(form.is_valid())

        # description
        form = TestForm(instance=page, data={"title": "title", "description": "desc\x00", "slug": "slug"})
        self.assertFalse(form.is_valid())

        # slug
        form = TestForm(instance=page, data={"title": "title", "description": "desc", "slug": "slug\x00"})
        self.assertFalse(form.is_valid())


class GetPageFormTestCase(InboxenTestCase):
    def test_valid_model(self):
        model_ct = ContentType.objects.get_for_model(models.HelpPage)
        form = forms.get_page_form(model_ct)

        self.assertEqual(form._meta.model, models.HelpPage)
        self.assertEqual(form.model_ct, model_ct)
        self.assertEqual(list(form.base_fields.keys()), [i for i in models.HelpPage.admin_fields])

    def test_invalid_model(self):
        model_ct = ContentType.objects.get_for_model(models.HelpBasePage)
        with self.assertRaises(AssertionError):
            forms.get_page_form(model_ct)

        model_ct = ContentType.objects.get_for_model(ContentType)
        with self.assertRaises(AssertionError):
            forms.get_page_form(model_ct)

        model_ct = ContentType.objects.get_for_model(models.HelpPage)
        with mock.patch.object(forms, "PAGE_TYPES", []), self.assertRaises(AssertionError):
            forms.get_page_form(model_ct)

        # double check the mock above is correctly undone itself
        self.assertTrue(len(forms.PAGE_TYPES))
