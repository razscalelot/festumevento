# Generated by Django 2.2.7 on 2022-10-21 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20221020_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('discount_on_total_bill', 'Discount On Total Bill'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('advance_and_discount_confirmation', 'Advance And Discount Confirmation')], max_length=50),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='permission_letter',
            field=models.FileField(blank=True, null=True, upload_to='media/file/permission_letter'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='poster',
            field=models.FileField(blank=True, null=True, upload_to='media/image/poster'),
        ),
        migrations.AlterField(
            model_name='orgdiscounts',
            name='discount_type',
            field=models.CharField(choices=[('discount_on_total_bill', 'Discount On Total Bill'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('advance_and_discount_confirmation', 'Advance And Discount Confirmation')], max_length=50),
        ),
    ]