# Generated by Django 2.2.7 on 2022-09-23 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20220923_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('discount_on_total_bill', 'Discount On Total Bill')], max_length=50),
        ),
        migrations.AlterField(
            model_name='orgequipment',
            name='orgequipment_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='orgequipment_id', to='api.SeatingArrangementBooking'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orgequipment',
            name='orgequipmentdiscounts',
            field=models.CharField(default=None, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orgequipment',
            name='orgequipmentdiscounts_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='orgequipmentdiscounts_id', to='api.OrgDiscounts'),
            preserve_default=False,
        ),
    ]
