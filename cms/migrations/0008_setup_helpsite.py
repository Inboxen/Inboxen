from django.conf import settings
from django.db import migrations


def initial_data(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")

    AppPage = apps.get_model("cms.AppPage")
    HelpIndex = apps.get_model("cms.HelpIndex")

    help_index_ct, _ = ContentType.objects.get_or_create(model="helpindex", app_label="cms")
    app_page_ct, _ = ContentType.objects.get_or_create(model="apppage", app_label="cms")

    help_index = HelpIndex.objects.create(
        title="Help & Support",
        description="",
        content_type=help_index_ct,
        slug="",
        lft=1,
        rght=4,
        tree_id=1,
        level=0,
    )

    questions_app = AppPage.objects.create(
        title="Questions",
        description="If you need assistance or want to speak to a human.",
        content_type=app_page_ct,
        app="tickets.urls",
        slug="questions",
        in_menu=True,
        parent=help_index,
        lft=2,
        rght=3,
        tree_id=1,
        level=1,
    )


def remove_initial_data(apps, schema_editor):
    HelpIndex = apps.get_model("cms.HelpIndex")
    AppPage = apps.get_model("cms.AppPage")

    HelpIndex.objects.all().delete()
    AppPage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0008_auto_20170916_2048"),
    ]

    operations = [
        migrations.RunPython(initial_data, remove_initial_data),
    ]
