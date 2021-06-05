# Generated by Django 3.2.3 on 2021-06-13 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Liberation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compression_type', models.PositiveSmallIntegerField(choices=[(0, 'Tarball (gzip compressed)'), (1, 'Tarball (bzip2 compression)'), (2, 'Tarball (no compression)')])),
                ('storage_type', models.PositiveSmallIntegerField(choices=[(0, 'Maildir'), (1, 'Mailbox .mbox')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('started', models.DateTimeField(null=True)),
                ('finished', models.DateTimeField(null=True)),
                ('errored', models.BooleanField(default=False)),
                ('error_message', models.CharField(max_length=255, null=True)),
                ('error_traceback', models.TextField(null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created', 'id'],
            },
        ),
    ]
