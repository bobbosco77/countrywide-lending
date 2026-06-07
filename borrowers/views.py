from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps

from .forms import BorrowerForm
from .models import Borrower, Loan, RepaymentSchedule, Payment
from .utils import log_action
from .permissions import (
    is_cashier,
    is_loan_officer,
    is_manager,
    is_auditor,
)

# ==================================================
# ROLE DECORATOR
# ==================================================

def role_required(check):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not check(request.user):
                return HttpResponse("Access Denied", status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================================================
# ROLE HELPERS
# ==================================================

def is_manager_or_superuser(user):
    return user.is_superuser or is_manager(user)


# ==================================================
# AUTH
# ==================================================

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user is not None:
            login(request, user)

            if user.is_superuser or is_manager(user):
                return redirect('dashboard')
            elif is_cashier(user):
                return redirect('borrower_list')
            elif is_auditor(user):
                return redirect('borrower_list')
            elif is_loan_officer(user):
                return redirect('register')
            else:
                return redirect('dashboard')

        messages.error(request, "Invalid credentials")
        return render(request, 'login.html')

    return render(request, 'login.html')

# ==================================================
# BORROWER
# ==================================================

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_loan_officer(u))
def register_borrower(request):
    form = BorrowerForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        borrower = form.save()

        log_action(
            request.user,
            'CREATE',
            borrower,
            f"Borrower {borrower} created"
        )

        return redirect('borrower_list')

    return render(request, 'register.html', {'form': form})


@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_cashier(u))
def borrower_list(request):
    borrowers = Borrower.objects.all()
    query = request.GET.get('q')

    if query:
        borrowers = borrowers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(nin__icontains=query) |
            Q(bvn__icontains=query)
        )

    return render(request, 'borrowers/borrower_list.html', {
        'borrowers': borrowers,
        'query': query
    })


@login_required
def borrower_profile(request, borrower_id):
    borrower = get_object_or_404(Borrower, id=borrower_id)

    loans = Loan.objects.filter(borrower=borrower)
    payments = Payment.objects.filter(loan__borrower=borrower)
    schedules = RepaymentSchedule.objects.filter(loan__borrower=borrower)

    return render(request, 'borrowers/profile.html', {
        'borrower': borrower,
        'loans': loans,
        'payments': payments,
        'schedules': schedules,
        'total_borrowed': sum(l.loan_amount for l in loans),
        'loan_balance': sum(l.balance() for l in loans),
    })


# ==================================================
# LOANS
# ==================================================

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_loan_officer(u))
def create_loan(request):
    if request.method == 'POST':
        borrower = get_object_or_404(Borrower, id=request.POST['borrower_id'])

        amount = Decimal(request.POST['loan_amount'])
        rate = Decimal(request.POST['interest_rate'])
        months = int(request.POST['duration_months'])

        loan = Loan.objects.create(
            borrower=borrower,
            loan_amount=amount,
            interest_rate=rate,
            duration_months=months,
            status='active'
        )

        interest = (amount * rate * months) / Decimal('100')
        total = amount + interest
        monthly = total / months

        for i in range(1, months + 1):
            RepaymentSchedule.objects.create(
                loan=loan,
                installment_number=i,
                due_date=date.today() + timedelta(days=30 * i),
                amount_due=monthly
            )

        log_action(request.user, 'LOAN', loan, f"Loan created {loan.id}")

        return redirect('loan_form')

    return render(request, 'loan_form.html')


# ==================================================
# PAYMENT
# ==================================================

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_cashier(u))
def make_payment(request):
    loans = Loan.objects.filter(status__in=['active', 'approved'])

    if request.method == 'POST':
        loan = get_object_or_404(Loan, id=request.POST['loan_id'])
        amount = Decimal(request.POST['amount_paid'])

        if amount <= 0:
            messages.error(request, "Payment must be greater than zero")
            return redirect('make_payment')

        Payment.objects.create(
            loan=loan,
            amount_paid=amount,
            method=request.POST.get('method', 'cash')
        )

        remaining = amount

        for s in RepaymentSchedule.objects.filter(loan=loan, status='pending'):
            if remaining >= s.amount_due:
                remaining -= s.amount_due
                s.status = 'paid'
                s.save()
            else:
                break

        if not RepaymentSchedule.objects.filter(loan=loan, status='pending').exists():
            loan.status = 'closed'
            loan.save()

        return redirect('loan_detail', loan.id)

    return render(request, 'borrowers/make_payment.html', {'loans': loans})


# ==================================================
# DASHBOARD
# ==================================================

@login_required
@role_required(is_manager_or_superuser)
def dashboard(request):
    return render(request, 'borrowers/dashboard.html', {
        'total_borrowers': Borrower.objects.count(),
        'active_loans': Loan.objects.filter(status='active').count(),
        'closed_loans': Loan.objects.filter(status='closed').count(),
        'pending_loans': Loan.objects.filter(status='pending').count(),
        'total_loan_portfolio': Loan.objects.aggregate(total=Sum('loan_amount'))['total'] or 0,
        'total_repayments': Payment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0,
        'loan_balance': sum(l.balance() for l in Loan.objects.all()),
    })


# ==================================================
# LOGIN / AUDIT / REPORTS
# ==================================================

@login_required
def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    return render(request, 'borrowers/loan_detail.html', {
        'loan': loan,
        'schedules': RepaymentSchedule.objects.filter(loan=loan),
        'payments': Payment.objects.filter(loan=loan),
    })


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_auditor(u))
def defaulters_report(request):

    overdue = RepaymentSchedule.objects.filter(
        status='pending',
        due_date__lt=date.today()
    )

    return render(
        request,
        'borrowers/defaulters.html',
        {
            'defaulters': overdue
        }
    )

@login_required
def loan_statement_pdf(request, loan_id):

    loan = get_object_or_404(Loan, id=loan_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="loan_{loan.id}.pdf"'
    )

    p = canvas.Canvas(response)

    p.drawString(200, 800, "LOAN STATEMENT")
    p.drawString(
        50,
        760,
        f"Borrower: {loan.borrower.first_name} {loan.borrower.last_name}"
    )
    p.drawString(
        50,
        740,
        f"Loan Amount: ₦{loan.loan_amount}"
    )
    p.drawString(
        50,
        720,
        f"Balance: ₦{loan.balance()}"
    )

    p.showPage()
    p.save()

    return response

@login_required
def borrowers_pdf(request):

    borrowers = Borrower.objects.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="borrowers_report.pdf"'
    )

    p = canvas.Canvas(response)

    p.drawString(200, 800, "BORROWERS REPORT")

    y = 760

    for borrower in borrowers:

        p.drawString(
            50,
            y,
            f"{borrower.first_name} {borrower.last_name}"
        )

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response