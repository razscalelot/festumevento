# Generated by Django 2.2.7 on 2022-09-23 08:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220923_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orgdiscounts',
            name='orgequipment',
        ),
        migrations.RemoveField(
            model_name='orgdiscounts',
            name='orgequipmentlist',
        ),
        migrations.AlterField(
            model_name='discounts',
            name='discount_type',
            field=models.CharField(choices=[('discount_on_equipment_or_item', 'Discount On Equipment Or Item'), ('advance_and_discount_confirmation', 'Advance And Discount Confirmation'), ('discount_on_total_bill', 'Discount On Total Bill')], max_length=50),
        ),
        migrations.CreateModel(
            name='OrgEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orgequipment', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('Oequipmentdiscounts_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Oequipmentdiscounts_id', to='api.OrgDiscounts')),
            ],
        ),
    ]