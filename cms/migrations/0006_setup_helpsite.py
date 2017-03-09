from django.conf import settings
from django.db import migrations


def initial_data(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")

    Collection = apps.get_model("wagtailcore.Collection")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")

    AppPage = apps.get_model("cms.AppPage")
    HelpIndex = apps.get_model("cms.HelpIndex")

    default_site = Site.objects.get()

    Collection.objects.create(
        name=settings.PEOPLE_PAGE_IMAGE_COLLECTION,
        path="00010001",
        depth=2,
        numchild=0,
    )
    Collection.objects.filter(path="0001").update(numchild=1)

    root_page = Page.objects.get(path="0001", slug="root")
    Page.objects.exclude(id=root_page.id).delete()

    help_index_ct, _ = ContentType.objects.get_or_create(model="helpindex", app_label="cms")
    app_page_ct, _ = ContentType.objects.get_or_create(model="apppage", app_label="cms")

    help_index = HelpIndex.objects.create(
        title="Help & Support",
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
        description="If you need assistance or want to speak to a human.",
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
        ("cms", "0006_peoplepage_intro_paragraph"),
        ("wagtailcore", "0032_add_bulk_delete_page_permission"),
        ("wagtaildocs", "0006_copy_document_permissions_to_collections"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(initial_data, remove_initial_data),
    ]
