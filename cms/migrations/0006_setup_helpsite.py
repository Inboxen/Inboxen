from django.conf import settings
from django.db import migrations


def initial_data(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Site = apps.get_model("wagtailcore.Site")
    HelpIndex = apps.get_model("cms.HelpIndex")
    AppPage = apps.get_model("cms.AppPage")
    Page = apps.get_model("wagtailcore.Page")

    default_site = Site.objects.get()

    root_page = Page.objects.get(path="0001", slug="root")
    Page.objects.exclude(id=root_page.id).delete()

    help_index_ct, _ = ContentType.objects.get_or_create(model="helpindex", app_label="cms")
    app_page_ct, _ = ContentType.objects.get_or_create(model="apppage", app_label="cms")

    help_index = HelpIndex.objects.create(
        title="Help",
        description="",
        depth=2,
        content_type=help_index_ct,
        path="00010001",
        numchild=1,
        slug="help",
        url_path="/help/",
    )

    questions_app = AppPage.objects.create(
        title="Questions",
        description="",
        depth=3,
        content_type=app_page_ct,
        path="000100010001",
        app="tickets.urls",
        slug="questions",
        url_path="/help/questions/",
        show_in_menus=True,
    )

    default_site.site_name = settings.SITE_NAME
    default_site.root_page = help_index
    default_site.is_default_site = True
    default_site.save()


def remove_initial_data(apps, schema_editor):
    HelpIndex = apps.get_model("cms.HelpIndex")
    AppPage = apps.get_model("cms.AppPage")

    HelpIndex.objects.all().delete()
    AppPage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0005_auto_20170226_2309"),
        ("wagtailcore", "0032_add_bulk_delete_page_permission"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(initial_data, remove_initial_data),
    ]
