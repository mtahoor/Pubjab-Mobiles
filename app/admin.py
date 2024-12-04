from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Reference)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Installment)
admin.site.register(Enrollment)
admin.site.register(Transaction)