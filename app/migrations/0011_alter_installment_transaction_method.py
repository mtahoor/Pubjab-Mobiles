# Generated by Django 5.1.3 on 2024-12-05 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_transaction_transaction_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installment',
            name='transaction_method',
            field=models.CharField(choices=[('cash', 'Cash'), ('bank', 'Bank'), ('jazz cash', 'Jazz Cash')], default='cash', max_length=10),
        ),
    ]