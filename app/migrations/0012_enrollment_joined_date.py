# Generated by Django 5.1.3 on 2025-02-03 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_installment_transaction_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='joined_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
