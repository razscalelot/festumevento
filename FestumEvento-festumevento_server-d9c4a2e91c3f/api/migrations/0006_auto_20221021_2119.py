# Generated by Django 2.2.7 on 2022-10-21 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20221021_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_total_bill', 'Discount On Total Bill'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item')], max_length=50),
        ),
        migrations.AlterField(
            model_name='eventcompanydetails',
            name='gst',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to='image/events/company/gst'),
        ),
        migrations.AlterField(
            model_name='eventvideo',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='media/video/thumbnail/events'),
        ),
        migrations.AlterField(
            model_name='orgdiscounts',
            name='discount_type',
            field=models.CharField(choices=[('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_total_bill', 'Discount On Total Bill'), ('discount_on_equipment_or_item', 'Discount On Equipment Or Item')], max_length=50),
        ),
    ]
