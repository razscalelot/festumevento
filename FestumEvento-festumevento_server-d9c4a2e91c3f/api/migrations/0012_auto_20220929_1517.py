# Generated by Django 2.2.7 on 2022-09-29 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20220929_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventregistration',
            name='poster',
            field=models.FileField(blank=True, null=True, upload_to='media/image/poster'),
        ),
    ]