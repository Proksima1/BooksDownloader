# Generated by Django 4.0.4 on 2022-08-10 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foundbook',
            name='bookPath',
        ),
    ]
