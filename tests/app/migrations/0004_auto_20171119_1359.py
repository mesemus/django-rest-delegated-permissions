# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-19 13:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_auto_20171117_1402'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_iteme', 'View Item E'),),
            },
        ),
        migrations.AlterField(
            model_name='container',
            name='item_c',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='container', to='app.ItemC'),
        ),
        migrations.AlterField(
            model_name='container',
            name='items_d',
            field=models.ManyToManyField(related_name='containers', to='app.ItemD'),
        ),
        migrations.AddField(
            model_name='iteme',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Container'),
        ),
    ]
