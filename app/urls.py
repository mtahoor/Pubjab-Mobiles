from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.custom_login, name='custom_login'),
    path('login/', views.custom_login, name='custom_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('add-staff-member/', views.add_staff_member, name='add_staff_member'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('activate/<int:user_id>/', views.activate_user, name='change_user_status'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/delete/<int:course_id>/', views.soft_delete_course, name='soft_delete_course'),
    path('references/', views.manage_references, name='manage_references'),
    path('references/delete/<int:reference_id>/', views.soft_delete_reference, name='soft_delete_reference'),
    path('students/', views.manage_students, name='manage_students'),
    path('students/<int:student_id>/', views.manage_students, name='edit_student'),
    path('students/delete/<int:student_id>/', views.soft_delete_student, name='soft_delete_student'),
    path('students/fees/', views.list_students_for_fee_payment, name='list_students_for_fee_payment'),
    path('students/fees/pay/<int:enrollment_id>/', views.pay_fee, name='pay_fee'),
    path('transactions/', views.list_transactions, name='list_transactions'),
    path('transactions/create/', views.create_transaction, name='create_transaction'),
    path('all_students/',views.all_students,name="all_students"),
    path('student/<int:student_id>/', views.student_details, name='student_details'),
    path('new-seats/', views.new_seats, name='new_seats'),
    path('installments-due/', views.installments_due, name='installments_due'),
    path('default-students/', views.default_students, name='default_students'),
    path('all-transactions/', views.all_transactions, name='all_transactions'), 
    path('change-staff-password/<int:user_id>/', views.change_staff_password, name='change_staff_password'),
    path('commision/', views.filter_students_data, name='filter_students_data'),
   
]
