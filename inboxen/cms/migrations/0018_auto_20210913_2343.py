# Generated by Django 3.2.4 on 2021-09-13 23:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0017_auto_20190501_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personinfo',
            name='image',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]
