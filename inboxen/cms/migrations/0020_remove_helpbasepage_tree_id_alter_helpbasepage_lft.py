# Generated by Django 4.2.4 on 2023-09-22 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0019_alter_helpbasepage_level_alter_helpbasepage_lft_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='helpbasepage',
            name='tree_id',
        ),
        migrations.AlterField(
            model_name='helpbasepage',
            name='lft',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]