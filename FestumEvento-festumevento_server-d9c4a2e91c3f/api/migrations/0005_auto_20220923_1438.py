# Generated by Django 2.2.7 on 2022-09-23 09:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20220923_1427'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orgequipment',
            name='Oequipmentdiscounts_id',
        ),
        migrations.RemoveField(
            model_name='orgequipment',
            name='id',
        ),
        migrations.AddField(
            model_name='orgequipment',
            name='orgequipmentId',
            field=models.AutoField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orgequipment',
            name='orgequipmentdiscounts_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orgequipmentdiscounts_id', to='api.OrgDiscounts'),
        ),
        migrations.AlterField(
            model_name='orgequipment',
            name='orgequipment_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orgequipment_id', to='api.SeatingArrangementBooking'),
        ),
    ]
