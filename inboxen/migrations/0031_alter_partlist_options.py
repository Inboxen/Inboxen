# Generated by Django 4.2.4 on 2023-09-22 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inboxen', '0030_alter_partlist_options_remove_partlist_tree_id_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partlist',
            options={'ordering': ['email', 'lft']},
        ),
    ]
