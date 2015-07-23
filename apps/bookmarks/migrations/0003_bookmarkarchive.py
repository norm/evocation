# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0002_bookmark_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookmarkArchive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('taken', models.DateTimeField(default=django.utils.timezone.now)),
                ('archive', models.FileField(null=True, upload_to=b'bookmark/%Y/%m/%d', blank=True)),
                ('screengrab', models.ImageField(null=True, upload_to=b'bookmark/%Y/%m/%d', blank=True)),
                ('thumbnail', models.ImageField(null=True, upload_to=b'bookmark/%Y/%m/%d', blank=True)),
                ('bookmark', models.ForeignKey(related_name='archives', to='bookmarks.Bookmark')),
            ],
            options={
                'ordering': ['-taken'],
            },
        ),
    ]
