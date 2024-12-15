from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.db.models import Q,Sum
from django.utils.timezone import now, timedelta
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.db.models import Min
from django.db.models import Count
import json
from django.db.models.functions import TruncDate


@login_required
def add_staff_member(request):
    if request.user.role != 'superuser': 
        return redirect('custom_login')

    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard') 
    else:
        form = StaffCreationForm()

    
    staff_users = CustomUser.objects.filter(role='staff')

    context={
        "staff_users":staff_users,
        "form":form
    }

    return render(request, 'admin/add_staff_member.html', context)


def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'superuser':
                    return redirect('admin_dashboard')  # Custom admin dashboard
                elif user.role == 'staff':
                    return redirect('staff_dashboard')  # Custom staff dashboard
        return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def admin_dashboard(request):
    if request.user.role != 'superuser':
        return redirect('custom_login')
    
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1) 
    else:
        date_from = now().date()

    # New Seats: Number of students registered today/this week
    new_seats = Student.objects.filter(created_at__date__gte=date_from).count()

    # Installments: Students with installments due today/this week
    installments_due = Installment.objects.filter(
        next_due_date__gte=date_from,
        next_due_date__lte=now().date(),
        payment_mode='installments'
    ).count()

    # Default Students: Students who missed due dates
    default_students = Installment.objects.filter(
        next_due_date__lt=now().date(),
        status='pending'
    ).count()

    # Deposit: Total incoming approved transactions + installments paid
    deposit_transactions = Transaction.objects.filter(
        transaction_type='incoming',
        status='approved',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    deposit_installments = Installment.objects.filter(
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    total_deposit = deposit_transactions + deposit_installments

    # Withdraw: Total outgoing approved transactions
    total_withdraw = Transaction.objects.filter(
        transaction_type='outgoing',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Pending Pays: Count of pending transactions and installments
    pending_transactions = Transaction.objects.filter(
        status='pending',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_installments = Installment.objects.filter(
        status='pending',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    pending_pays = pending_transactions + pending_installments

    # Total: Deposit minus Withdraw
    total_balance = (total_deposit - total_withdraw)-pending_pays

    tt_balance = total_balance+pending_pays

    # Bank and Cash Splits for Approved Payments
    bank_amount = Installment.objects.filter(
        transaction_method='bank',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    cash_amount = Installment.objects.filter(
        transaction_method='cash',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0






    # Fetch all pending installments and transactions
    pending_installments = Installment.objects.filter(status='pending')
    pending_transactions = Transaction.objects.filter(status='pending')

    # Combine results into a single list
    pending_payments = []

    # Add installments to the list
    for installment in pending_installments:
        pending_payments.append({
            'id': f'installment-{installment.id}',
            'type': 'Installment',
            'description': f"Course Fee -{installment.enrollment.student.roll_number}-{installment.enrollment.student.name}",
            'amount': installment.amount_paid,
            'received_by': installment.collected_by.username if installment.collected_by else 'N/A',
            'payment_method': installment.transaction_method.capitalize(),
            'status': installment.status,
            'model': 'installment'
        })

    # Add transactions to the list
    for transaction in pending_transactions:
        pending_payments.append({
            'id': f'transaction-{transaction.id}',
            'type': 'Expense' if transaction.transaction_type == 'outgoing' else 'Income',
            'description': transaction.description,
            'amount': transaction.amount,
            'received_by': transaction.created_by.username if transaction.created_by else 'N/A',
            'payment_method': transaction.transaction_method,
            'status': transaction.status,
            'model': 'transaction'
        })

    # Handle form submission
    if request.method == 'POST':
        for record in pending_payments:
            record_id = record['id']
            model_type, obj_id = record_id.split('-')

            # Check if the record is approved in the form
            if f'approve_record_{record_id}' in request.POST:
                if model_type == 'installment':
                    installment = Installment.objects.get(id=obj_id)
                    installment.status = 'approved'
                    installment.save()
                elif model_type == 'transaction':
                    transaction = Transaction.objects.get(id=obj_id)
                    transaction.status = 'approved'
                    transaction.save()

        return redirect('admin_dashboard')








    context = {
        'new_seats': new_seats,
        'installments_due': installments_due,
        'default_students': default_students,
        'total_deposit': total_deposit,
        'total_withdraw': total_withdraw,
        'pending_pays': pending_pays,
        'total_balance': total_balance,
        'bank_amount': bank_amount,
        'cash_amount': cash_amount,
        'filter_type': filter_type,
        'pending_payments': pending_payments,
        'tt_balance':tt_balance
    }
    return render(request, 'admin/admin_dashboard.html',context)

@login_required
def staff_dashboard(request):
    if request.user.role != 'staff':
        return redirect('custom_login')
    
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1)
    else:
        date_from = now().date()

    # New Seats: Number of students registered today/this week
    new_seats = Student.objects.filter(created_at__date__gte=date_from).count()

    # Installments: Students with installments due today/this week
    installments_due = Installment.objects.filter(
        next_due_date__gte=date_from,
        next_due_date__lte=now().date(),
        payment_mode='installments'
    ).count()

    # Default Students: Students who missed due dates
    default_students = Installment.objects.filter(
        next_due_date__lt=now().date(),
        status='pending'
    ).count()

    # Deposit: Total incoming approved transactions + installments paid
    deposit_transactions = Transaction.objects.filter(
        transaction_type='incoming',
        status='approved',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    deposit_installments = Installment.objects.filter(
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    total_deposit = deposit_transactions + deposit_installments

    # Withdraw: Total outgoing approved transactions
    total_withdraw = Transaction.objects.filter(
        transaction_type='outgoing',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Pending Pays: Count of pending transactions and installments
    pending_transactions = Transaction.objects.filter(
        status='pending',
        created_at__date__gte=date_from
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_installments = Installment.objects.filter(
        status='pending',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    pending_pays = pending_transactions + pending_installments

    # Total: Deposit minus Withdraw
    total_balance = (total_deposit - total_withdraw)-pending_pays

    tt_balance = total_balance+pending_pays

    # Bank and Cash Splits for Approved Payments
    bank_amount = Installment.objects.filter(
        transaction_method='bank',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    cash_amount = Installment.objects.filter(
        transaction_method='cash',
        date_paid__gte=date_from
    ).aggregate(total=Sum('amount_paid'))['total'] or 0



    context = {
        'new_seats': new_seats,
        'installments_due': installments_due,
        'default_students': default_students,
        'total_deposit': total_deposit,
        'total_withdraw': total_withdraw,
        'pending_pays': pending_pays,
        'total_balance': total_balance,
        'bank_amount': bank_amount,
        'cash_amount': cash_amount,
        'filter_type': filter_type,
        'tt_balance':tt_balance
    }
    
    return render(request, 'staff/staff_dashboard.html',context)


@login_required
def activate_user(request, user_id):

    if request.user.role != 'superuser': 
        return redirect('custom_login')
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin/admin_dashboard')



@login_required
def manage_courses(request):

    if request.user.role != 'superuser': 
        return redirect('custom_login')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_courses')  
    else:
        form = CourseForm()
    courses = Course.objects.all_with_deleted()
    context = {
        'form': form,
        'courses': courses,
    }
    return render(request, 'admin/manage_courses.html', context)

@login_required
def soft_delete_course(request, course_id):
    if request.user.role != 'superuser': 
        return redirect('custom_login')
    course = Course.objects.all_with_deleted().get(id=course_id)
    course.is_deleted = not course.is_deleted
    course.save()
    return redirect('manage_courses')  


@login_required
def manage_references(request):
    if request.user.role != 'superuser': 
        return redirect('custom_login')
    if request.method == 'POST':
        form = ReferenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_references')  
    else:
        form = ReferenceForm()
    references = Reference.objects.all_with_deleted()
    context = {
        'form': form,
        'references': references,
    }
    return render(request, 'admin/manage_references.html', context)


@login_required
def soft_delete_reference(request, reference_id):
    if request.user.role != 'superuser': 
        return redirect('custom_login')
    reference = Reference.objects.all_with_deleted().get(id=reference_id)
    reference.is_deleted = not reference.is_deleted  
    reference.save()
    return redirect('manage_references')  



@login_required
def manage_students(request, student_id=None):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    # Handle edit mode if a student_id is provided
    if student_id:
        student = get_object_or_404(Student, id=student_id)
        enrollment = Enrollment.objects.filter(student=student).first()
        installment = Installment.objects.filter(enrollment=enrollment).first()

        student_form = StudentForm(instance=student)
        enrollment_form = EnrollmentForm(instance=enrollment)
        installment_form = InstallmentForm(instance=installment)

        button_text = "Update Student"
    else:
        student_form = StudentForm()
        enrollment_form = EnrollmentForm()
        installment_form = InstallmentForm()

        button_text = "Add Student"

    if request.method == 'POST':
        # Handle form submissions
        student_form = StudentForm(request.POST, request.FILES, instance=student if student_id else None)
        enrollment_form = EnrollmentForm(request.POST, instance=enrollment if student_id else None)
        installment_form = InstallmentForm(request.POST, instance=installment if student_id else None)

        if student_form.is_valid() and enrollment_form.is_valid():
            # Save student
            student = student_form.save(commit=False)
            student.who_enrolled = request.user  # Assign current user
            student.save()

            # Save enrollment
            enrollment = enrollment_form.save(commit=False)
            enrollment.student = student
            enrollment.created_by = request.user
            enrollment.save()

            # Handle installment logic
            if installment_form.is_valid():
                installment = installment_form.save(commit=False)
                installment.enrollment = enrollment
                installment.collected_by = request.user

                # Handle "Pay in Full" case
                if installment.payment_mode == "pay_in_full":
                    remaining_fee = enrollment.course_fee
                    installment.amount_paid = remaining_fee
                    installment.next_due_date = None  # No next due date for "Pay in Full"

                    # Update enrollment status
                    enrollment.enrollment_status = "paid"
                    enrollment.save()

                # Save installment
                installment.save()

            return redirect('manage_students')

    # Fetch students for the table
    students = Student.objects.all_with_deleted().order_by('-id')  # Newest first

    context = {
        'student_form': student_form,
        'enrollment_form': enrollment_form,
        'installment_form': installment_form,
        'students': students,
        'button_text': button_text,
        'base':base_template
    }
    return render(request, 'admin/manage_students.html', context)


@login_required
def soft_delete_student(request, student_id):
    if request.user.role != 'superuser': 
        return redirect('custom_login')
    student = Student.objects.all_with_deleted().get(id=student_id)
    student.is_deleted = not student.is_deleted  # Toggle soft delete
    student.save()
    return redirect('all_students')


@login_required
def list_students_for_fee_payment(request):
    # Set base template
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'

    # Handle search query
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) |
            Q(cnic__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(roll_number__icontains=query),
            is_deleted=False,
            enrollment__enrollment_status='payment_pending'
        ).distinct()
    else:
        students = Student.objects.filter(
            is_deleted=False,
            enrollment__enrollment_status='payment_pending'
        ).distinct()

    # Annotate total_paid and remaining_fee for each student
    students_with_fees = []
    for student in students:
        student_enrollments = student.enrollment_set.all()
        for enrollment in student_enrollments:
            total_paid = enrollment.installment_set.filter().aggregate(
                total=Sum('amount_paid')
            )['total'] or 0
            remaining_fee = enrollment.course_fee - total_paid

            students_with_fees.append({
                'student': student,
                'enrollment': enrollment,
                'total_paid': total_paid,
                'remaining_fee': remaining_fee,
            })

    context = {
        'students_with_fees': students_with_fees,
        'query': query,
        'base': base_template
    }
    return render(request, 'admin/list_students_fee.html', context)



@login_required
def pay_fee(request, enrollment_id):

    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    total_paid = Installment.objects.filter(enrollment=enrollment).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    remaining_fee = enrollment.course_fee - total_paid

    if request.method == 'POST':
        form = InstallmentForm(request.POST)
        if form.is_valid():
            installment = form.save(commit=False)
            installment.enrollment = enrollment
            installment.collected_by = request.user

            if installment.payment_mode == 'pay_in_full':
                installment.amount_paid = remaining_fee
                installment.next_due_date = None
                enrollment.enrollment_status = 'paid'
                enrollment.save()
            else:
                if installment.amount_paid >= remaining_fee:
                    enrollment.enrollment_status = 'paid'
                    installment.next_due_date = None
                enrollment.save()

            installment.save()
            return redirect('list_students_for_fee_payment')

    else:
        form = InstallmentForm()

    context = {
        'enrollment': enrollment,
        'remaining_fee': remaining_fee,
        'form': form,
        'base': base_template
    }
    return render(request, 'admin/pay_fee.html', context)



@login_required
def create_transaction(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)  # Do not commit yet
            transaction.created_by = request.user  # Assign the user
            transaction.save() 
            return redirect('list_transactions')
    else:
        form = TransactionForm()

    context = {
        'form': form,
        'base':base_template
    }
    return render(request, 'admin/create_transaction.html', context)


@login_required
def list_transactions(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    
    transactions = Transaction.objects.all().order_by('-created_at')
    context = {
        'transactions': transactions,
        'base': base_template
    }
    return render(request, 'admin/list_transactions.html', context)


@login_required
def all_students(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.all_with_deleted().filter(
            Q(name__icontains=query) |
            Q(cnic__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(roll_number__icontains=query)
        )
    else:
        students = Student.objects.all_with_deleted().order_by('-id')


    context = {
        'students': students,
        'base': base_template
    }
    return render(request, 'admin/all_students.html', context)

@login_required
def student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    enrollments = Enrollment.objects.filter(student=student)

    total_paid = Installment.objects.filter(enrollment__student=student).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    remaining_fee = sum(enrollment.course_fee for enrollment in enrollments) - total_paid

    installments = Installment.objects.filter(enrollment__student=student).select_related('collected_by', 'enrollment')

    context = {
        'student': student,
        'enrollments': enrollments,
        'installments': installments,
        'total_fee': sum(enrollment.course_fee for enrollment in enrollments),
        'total_paid': total_paid,
        'remaining_fee': remaining_fee,
    }
    return render(request, 'admin/student_details.html', context)



@login_required
def new_seats(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'

    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1)
    else:
        date_from = now().date()
    students =  Student.objects.filter(created_at__date__gte=date_from).order_by('-id')
    context = {'students': students,'base':base_template,'filter_type':filter_type}
    return render(request, 'admin/new_seats.html', context)

@login_required
def installments_due(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1)
    else:
        date_from = now().date()
    installments = Installment.objects.filter(
        next_due_date__gte=date_from,
        next_due_date__lte=now().date(),
        payment_mode='installments'
    )
    context = {'installments': installments,'base':base_template,'filter_type':filter_type}
    return render(request, 'admin/installments_due.html', context)

@login_required
def default_students(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1)
    else:
        date_from = now().date()
    installments = Installment.objects.filter(
        next_due_date__gte=date_from,
        next_due_date__lt=now().date(),
        status='pending'
    ).select_related('enrollment__student', 'enrollment__course')

    # Calculate the remaining fee for each installment's course
    for installment in installments:
        total_paid = Installment.objects.filter(
            enrollment=installment.enrollment,
            # status='approved'  # Only approved payments count
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        installment.remaining_fee = installment.enrollment.course_fee - total_paid


    context = {'installments': installments,'base':base_template,'filter_type':filter_type}
    return render(request, 'admin/default_students.html', context)


@login_required
def all_transactions(request):
    if request.user.role == 'staff':
        base_template = 'base/staff_base.html'
    else:
        base_template = 'base/base.html'
    # Determine the filter type
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        date_from = now().date()
    elif filter_type == 'weekly':
        date_from = now().date() - timedelta(days=7)
    elif filter_type == 'monthly':
        date_from = now().replace(day=1)
    else:
        date_from = now().date()

    # Fetch filtered transactions (approved and pending within the date range)
    transactions = Transaction.objects.filter(created_at__date__gte=date_from)

    # Fetch filtered installments (approved and pending within the date range)
    installments = Installment.objects.filter(date_paid__gte=date_from).select_related('enrollment__student', 'collected_by')

    # Calculate the total balance
    approved_transactions = transactions.filter()
    approved_installments = installments.filter()

    # Total Income from approved incoming transactions
    total_income = approved_transactions.filter(transaction_type='incoming').aggregate(Sum('amount'))['amount__sum'] or 0

    # Total Expenses from approved outgoing transactions
    total_expense = approved_transactions.filter(transaction_type='outgoing').aggregate(Sum('amount'))['amount__sum'] or 0

    # Total Installments received (approved only)
    total_installments = approved_installments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # Calculate total balance
    total_balance = (total_income + total_installments) - total_expense

    context = {
        'transactions': transactions,
        'installments': installments,
        'total_balance': total_balance,
        'filter_type': filter_type,
        'base':base_template
    }
    return render(request, 'admin/all_transactions.html', context)


@login_required
def change_staff_password(request, user_id):
    if request.user.role != 'superuser': 
        return redirect('custom_login')
    staff_user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            staff_user.password = make_password(new_password)  # Hash the new password
            staff_user.save()
            return redirect('add_staff_member')  # Redirect to the staff management page
    else:
        form = ChangePasswordForm()

    context = {
        'staff_user': staff_user,
        'form': form
    }
    return render(request, 'admin/change_staff_password.html', context)


def filter_students_data(request):
    # Get current date
    today = now().date()

    # Define time filters for current and previous months
    months = [
        today.replace(day=1),  # Current month
        (today.replace(day=1) - timedelta(days=1)).replace(day=1),  # Previous month
        ((today.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1)).replace(day=1),
        (((today.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1)),
    ]

    # Default selections
    selected_month = request.GET.get('month', months[0].strftime('%Y-%m'))
    filter_type = request.GET.get('filter_type', 'reference')  # 'reference' or 'registered_by'
    filter_value = request.GET.get('filter_value', None)

    # Filter by selected month
    selected_month_start = now().replace(year=int(selected_month.split('-')[0]), month=int(selected_month.split('-')[1]), day=1)
    next_month = (selected_month_start + timedelta(days=31)).replace(day=1)
    
    students = Student.objects.filter(
        created_at__gte=selected_month_start,
        created_at__lt=next_month,
    )

    # Apply additional filters
    if filter_type == 'reference' and filter_value:
        students = students.filter(reference_id=filter_value)
    elif filter_type == 'registered_by' and filter_value:
        students = students.filter(who_enrolled_id=filter_value)

    # Group data by date
    student_counts = students.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')

    # Convert student_counts to a JSON-serializable list
    student_counts_list = [
        {'date': entry['date'].strftime('%Y-%m-%d') if entry['date'] else None, 'count': entry['count']}
        for entry in student_counts
    ]
    # Prepare dropdowns
    references = Reference.objects.all()
    users = CustomUser.objects.filter(role__in=['staff', 'admin'])

    context = {
        'months': [(month.strftime('%Y-%m'), month.strftime('%B')) for month in months],
        'selected_month': selected_month,
        'filter_type': filter_type,
        'filter_value': filter_value,
        'references': references,
        'users': users,
        'student_counts': student_counts_list,
        'total_count': students.count(),
        'chart_data': json.dumps(student_counts_list), 
        
    }
    return render(request, 'admin/filter_students.html', context)