from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from .managers import CustomUserManager,SoftDeleteManager
from django.db.models import Max

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='superuser')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    cnic = models.CharField(max_length=15, null=True, blank=True,unique=True) 
    phone_number = models.CharField(max_length=15, null=True, blank=True)  

    objects = CustomUserManager()


class Course(models.Model):
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def __str__(self):
        return self.name


class Reference(models.Model):
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def __str__(self):
        return self.name


class Student(models.Model):
    picture = models.ImageField(upload_to='students_pictures/', null=True, blank=True)
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    cnic = models.CharField(max_length=15,null=True,blank=True)
    phone_number = models.CharField(max_length=15)
    father_phone_number = models.CharField(max_length=15,null=True,blank=True)
    who_enrolled = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    enrollment_method = models.CharField(max_length=50, choices=[('call', 'Call'), ('visitor', 'Visitor')])
    reference = models.ForeignKey('Reference', on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False)
    roll_number = models.CharField(max_length=10, unique=True, editable=False,null=True,blank=True)
    created_at = models.DateTimeField(default=now)

    objects = SoftDeleteManager()

    def save(self, *args, **kwargs):
        if not self.roll_number:
            current_month_year = now().strftime('%y%m') 
            highest_roll_number = Student.objects.all_with_deleted().filter(
                roll_number__startswith=f"{current_month_year}-"  
            ).aggregate(
                highest=Max('roll_number')
            )['highest']
            if highest_roll_number:
                current_sequence = int(highest_roll_number.split('-')[-1])
                next_sequence = current_sequence + 1
            else:
                next_sequence = 1
            self.roll_number = f"{current_month_year}-{next_sequence}"
            print("Generated Roll Number:", self.roll_number)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_fee = models.FloatField()
    enrollment_status = models.CharField(
        max_length=20,
        choices=[('payment_pending', 'Payment Pending'), ('paid', 'Paid')],
        default='payment_pending'
    )
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=now)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"


class Installment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('jazz cash','Jazz Cash'),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    payment_mode = models.CharField(
        max_length=50,
        choices=[('pay_in_full', 'Pay in Full'), ('installments', 'Installments')]
    )
    amount_paid = models.FloatField(null=True, blank=True)  # Only needed for installments
    date_paid = models.DateField(auto_now_add=True)
    next_due_date = models.DateField(null=True, blank=True)  # Only applicable for installments
    collected_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=now)
    transaction_method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default='cash'  # Default to cash
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'  # Default to pending
    )
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    def __str__(self):
        return f"{self.enrollment.student.name} - {self.amount_paid} ({self.status})"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
    ]

    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('jazz cash','Jazz Cash'),
    ]

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default='outgoing'
    )
    transaction_method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        default='cash'  # Default to cash
    )
    amount = models.FloatField()
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(default=now)
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount} ({self.status})"
