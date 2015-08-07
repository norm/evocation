# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0004_auto_20150728_0645'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=2000)),
                ('favicon', models.ImageField(null=True, upload_to=b'favicon/', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='bookmark',
            name='site',
            field=models.ForeignKey(related_name='bookmarks', blank=True, to='bookmarks.Website', null=True),
        ),
    ]
