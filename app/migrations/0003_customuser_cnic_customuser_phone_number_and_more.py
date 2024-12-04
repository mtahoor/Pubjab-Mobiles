# Generated by Django 5.1.3 on 2024-11-25 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_customuser_managers_customuser_is_staff_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cnic',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('superuser', 'Superuser'), ('staff', 'Staff')], default='superuser', max_length=20),
        ),
    ]