# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0005_auto_20150807_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmark',
            name='origin',
            field=models.IntegerField(default=1, choices=[(1, b'User'), (2, b'Pinboard')]),
        ),
    ]
