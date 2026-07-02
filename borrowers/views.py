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
import json
import openpyxl

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
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.get_full_name() or user.username}!"
            )

            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            if user.is_superuser or is_manager(user):
                return redirect("dashboard")

            elif is_cashier(user):
                return redirect("borrower_list")

            elif is_auditor(user):
                return redirect("defaulters_report")

            elif is_loan_officer(user):
                return redirect("register")

            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

# ==================================================
# BORROWER
# ==================================================

@login_required
@role_required(
    lambda u:
    is_manager_or_superuser(u)
    or is_cashier(u)
    or is_loan_officer(u)
)
def register_borrower(request):

    form = BorrowerForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and form.is_valid():

        borrower = form.save()

        log_action(
            request.user,
            'CREATE',
            borrower,
            f"Borrower {borrower} created"
        )

        # Loan Officer returns to registration page
        if is_loan_officer(request.user):
            messages.success(
                request,
                "Borrower registered successfully."
            )
            return redirect('register')

        # Cashier and Manager go to borrower list
        return redirect('borrower_list')

    return render(
        request,
        'register.html',
        {'form': form}
    )

@login_required
@role_required(
    lambda u:
    is_manager_or_superuser(u)
    or is_cashier(u)
    or is_auditor(u)
)
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

    return render(
        request,
        'borrowers/borrower_list.html',
        {
            'borrowers': borrowers,
            'query': query
        }
    )


@login_required
def borrower_profile(request, borrower_id):
    borrower = get_object_or_404(Borrower, id=borrower_id)

    loans = (
        Loan.objects
        .filter(borrower=borrower)
        .order_by("-start_date")
    )

    payments = (
        Payment.objects
        .filter(loan__borrower=borrower)
        .select_related("loan")
        .order_by("-payment_date")
    )

    schedules = (
        RepaymentSchedule.objects
        .filter(loan__borrower=borrower)
    )

    total_borrowed = sum(
        loan.loan_amount
        for loan in loans
    )

    total_balance = sum(
        loan.balance()
        for loan in loans
    )

    return render(
        request,
        "borrowers/profile.html",
        {
            "borrower": borrower,
            "loans": loans,
            "payments": payments,
            "schedules": schedules,
            "total_borrowed": total_borrowed,
            "loan_balance": total_balance,
        }
    )


# ==================================================
# LOANS
# ==================================================

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_loan_officer(u))
def create_loan(request):

    borrowers = Borrower.objects.order_by("first_name", "last_name")

    if request.method == "POST":

        borrower = get_object_or_404(
            Borrower,
            id=request.POST.get("borrower_id")
        )

        amount = Decimal(request.POST.get("loan_amount"))
        rate = Decimal(request.POST.get("interest_rate"))
        weeks = int(request.POST['duration_weeks'])

        loan = Loan.objects.create(
            borrower=borrower,
            loan_amount=amount,
            interest_rate=rate,
            duration_weeks=weeks,
            status="active"
        )

        # Generate repayment schedule
        loan.generate_repayment_schedule()

        log_action(
            request.user,
            "LOAN",
            loan,
            f"Loan #{loan.id} created for {borrower.first_name} {borrower.last_name}"
        )

        messages.success(
            request,
            "Loan created successfully."
        )

        return redirect("loan_form")

    return render(
        request,
        "loan_form.html",
        {
            "borrowers": borrowers,
        }
    )


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

        payment = Payment.objects.create(
            loan=loan,
            amount_paid=amount,
            method=request.POST.get('method', 'cash')
        )


        return redirect('payment_receipt', payment.id)
    return render(request, 'borrowers/make_payment.html', {'loans': loans})

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_cashier(u))
def payment_receipt(request, payment_id):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "loan",
            "loan__borrower"
        ),
        id=payment_id
    )

    loan = payment.loan

    context = {
        "payment": payment,
        "loan": loan,
        "borrower": loan.borrower,
        "total_paid": loan.total_paid(),
        "balance": loan.balance(),
    }

    return render(
        request,
        "borrowers/receipt.html",
        context
    )



# ==================================================
# DASHBOARD
# ==================================================

@login_required
@role_required(is_manager_or_superuser)
def dashboard(request):

    recent_loans = (
        Loan.objects
        .select_related("borrower")
        .order_by("-id")[:5]
    )

    recent_payments = (
        Payment.objects
        .select_related("loan", "loan__borrower")
        .order_by("-id")[:5]
    )

    context = {
        "total_borrowers": Borrower.objects.count(),
        "active_loans": Loan.objects.filter(status="active").count(),
        "closed_loans": Loan.objects.filter(status="closed").count(),
        "pending_loans": Loan.objects.filter(status="pending").count(),
        "total_loan_portfolio": Loan.objects.aggregate(
            total=Sum("loan_amount")
        )["total"] or 0,
        "total_repayments": Payment.objects.aggregate(
            total=Sum("amount_paid")
        )["total"] or 0,
        "loan_balance": sum(
            loan.balance() for loan in Loan.objects.all()
        ),
        "recent_loans": recent_loans,
        "recent_payments": recent_payments,
    }

    return render(
        request,
        "borrowers/dashboard.html",
        context
    )

# ==================================================
# LOGIN / AUDIT / REPORTS
# ==================================================

@login_required
def loan_detail(request, loan_id):

    loan = get_object_or_404(
        Loan.objects.select_related("borrower"),
        id=loan_id
    )

    schedules = (
        RepaymentSchedule.objects
        .filter(loan=loan)
        .order_by("installment_number")
    )

    payments = (
        Payment.objects
        .filter(loan=loan)
        .order_by("-payment_date")
    )

    total_paid = loan.total_paid()
    total_repayment = loan.total_repayment()
    balance = loan.balance()

    total_installments = schedules.count()
    paid_installments = schedules.filter(status="paid").count()

    # Progress based on amount paid
    progress = 0

    if total_repayment > 0:
        progress = round(
            float((total_paid / total_repayment) * 100),
            1
        )

    # Never exceed 100%
    progress = min(progress, 100)

    context = {
        "loan": loan,
        "schedules": schedules,
        "payments": payments,
        "total_paid": total_paid,
        "total_repayment": total_repayment,
        "balance": balance,
        "total_installments": total_installments,
        "paid_installments": paid_installments,
        "progress": progress,
    }

    return render(
        request,
        "borrowers/loan_detail.html",
        context,
    )


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_auditor(u))
def defaulters_report(request):

    overdue = RepaymentSchedule.objects.select_related(
        'loan',
        'loan__borrower'
    ).filter(
        status='pending',
        due_date__lt=date.today()
    )

    search = request.GET.get('search')

    if search:
        overdue = overdue.filter(
            Q(loan__borrower__first_name__icontains=search) |
            Q(loan__borrower__last_name__icontains=search) |
            Q(loan__borrower__phone__icontains=search)
        )

    for item in overdue:
        item.days_overdue = (date.today() - item.due_date).days

    chart_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    chart_data = [0,0,0,0,0,0,0]

    context = {
        "defaulters": overdue,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "officers": [],   # keeps your template working
    }

    return render(
        request,
        "borrowers/defaulters.html",
        context
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
    p.drawString(
        50,
        700,
        f"Duration: {loan.duration_weeks} Weeks"
    )

    p.showPage()
    p.save()

    return response

@login_required
@role_required(
    lambda u:
    is_manager_or_superuser(u)
    or is_auditor(u)
)
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


@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_auditor(u))
def export_defaulters_excel(request):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Defaulters"

    ws.append(["Borrower", "Phone", "Amount Due", "Due Date"])

    defaulters = RepaymentSchedule.objects.filter(
        due_date__lt=date.today()
    ).exclude(status='paid')

    for item in defaulters:
        ws.append([
            f"{item.loan.borrower.first_name} {item.loan.borrower.last_name}",
            item.loan.borrower.phone,
            item.amount_due,
            item.due_date,
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=defaulters.xlsx'

    wb.save(response)
    return response

@login_required
@role_required(lambda u: is_manager_or_superuser(u) or is_auditor(u))
def export_defaulters_pdf(request):

    overdue = RepaymentSchedule.objects.filter(
        status='pending',
        due_date__lt=date.today()
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="defaulters.pdf"'

    p = canvas.Canvas(response)

    p.drawString(200, 800, "DEFAULTERS REPORT")

    y = 760
    for item in overdue:
        p.drawString(
            50, y,
            f"{item.loan.borrower.first_name} {item.loan.borrower.last_name} - ₦{item.amount_due}"
        )
        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()
    return response