# Generated by Django 5.1.3 on 2024-12-02 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_course_reference_enrollment_installment_student_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='cnic',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='cnic',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='father_phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
