# Generated by Django 4.0.4 on 2022-08-18 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='bookName',
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name='searchrequest',
            name='searchRequest',
            field=models.TextField(unique=True),
        ),
    ]
