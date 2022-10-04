# Generated by Django 2.2.7 on 2022-09-30 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20220929_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('discount_on_total_bill', 'Discount On Total Bill'), ('advance_and_discount_confirmation', 'Advance And Discount Confirmation')], max_length=50),
        ),
        migrations.AlterField(
            model_name='eventcompanyvideo',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='image/events/company/video'),
        ),
    ]