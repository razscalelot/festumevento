# Generated by Django 2.2.7 on 2022-11-09 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20221108_1000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('discount_on_total_bill', 'Discount On Total Bill')], max_length=50),
        ),
        migrations.AlterField(
            model_name='orgdiscounts',
            name='discount_type',
            field=models.CharField(choices=[('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('discount_on_total_bill', 'Discount On Total Bill')], max_length=50),
        ),
    ]