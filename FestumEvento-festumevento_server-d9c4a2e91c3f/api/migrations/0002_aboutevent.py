# Generated by Django 2.2.7 on 2022-09-06 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_to_end_date', models.CharField(max_length=255)),
                ('start_time', models.CharField(max_length=100)),
                ('end_time', models.CharField(max_length=100)),
                ('about_event', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='about', to='api.Event')),
            ],
        ),
    ]