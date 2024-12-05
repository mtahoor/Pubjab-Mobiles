from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import *


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))





class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        }),
        label="Password"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'cnic', 'phone_number', 'username', 'password']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'cnic': 'CNIC',
            'phone_number': 'Phone Number',
            'username': 'Username',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Last Name'
            }),
            'cnic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter CNIC'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Username'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  
        user.role = 'staff' 
        user.is_staff = True 
        if commit:
            user.save()
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Course Name'
            }),
        }
        labels = {
            'name': 'Course Name',
        }

class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Reference Name'
            }),
        }
        labels = {
            'name': 'Reference Name',
        }


# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = ['picture', 'name', 'father_name', 'cnic', 'phone_number', 'father_phone_number', 'enrollment_method', 'reference']
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Student Name'}),
#             'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Father Name'}),
#             'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CNIC'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
#             'father_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Father Phone Number'}),
#             'enrollment_method': forms.Select(attrs={'class': 'form-control'}),
#             'reference': forms.Select(attrs={'class': 'form-control'}),
#             'picture': forms.FileInput(attrs={'class': 'form-control'}),
#         }
#         labels = {
#             'name': 'Student Name',
#             'father_name': 'Father Name',
#             'cnic': 'CNIC',
#             'phone_number': 'Phone Number',
#             'father_phone_number': 'Father Phone Number',
#             'enrollment_method': 'Enrollment Method',
#             'reference': 'Reference',
#             'picture': 'Picture',
#         }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'picture', 'name', 'father_name', 'cnic', 'phone_number',
            'father_phone_number', 'enrollment_method', 'reference'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Student Name'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Father Name'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CNIC'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'father_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Father Phone Number'}),
            'enrollment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference': forms.Select(attrs={'class': 'form-control'}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'course_fee']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'course_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Course Fee'}),
        }


class InstallmentForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ['payment_mode', 'amount_paid', 'next_due_date', 'transaction_method' ]
        widgets = {
            'payment_mode': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleInstallmentFields()'  # Add JS handler
            }),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transaction_method': forms.Select(attrs={'class': 'form-control'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description','transaction_method']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
            'transaction_method': forms.Select(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        label='New Password'
    )
