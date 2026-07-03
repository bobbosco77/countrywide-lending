from decimal import Decimal

import openpyxl

from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone

from .models import Loan, Payment, Borrower


def loan_register_excel(request):

    wb = openpyxl.Workbook()

    ws = wb.active

    ws.title = "Loan Register"

    ws.append([
        "Loan ID",
        "Borrower",
        "Phone",
        "Loan Amount",
        "Amount Paid",
        "Outstanding",
        "Interest %",
        "Weeks",
        "Status",
        "Date",
    ])

    loans = (
        Loan.objects
        .select_related("borrower")
        .order_by("-start_date")
    )

    for loan in loans:

        ws.append([

            loan.id,

            f"{loan.borrower.first_name} {loan.borrower.last_name}",

            loan.borrower.phone,

            float(loan.loan_amount),

            float(loan.total_paid()),

            float(loan.balance()),

            float(loan.interest_rate),

            loan.duration_weeks,

            loan.status,

            loan.start_date.strftime("%d-%m-%Y"),

        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="Loan_Register.xlsx"'

    wb.save(response)

    return response

def payment_register_excel(request):

    wb = openpyxl.Workbook()

    ws = wb.active

    ws.title = "Payment Register"

    ws.append([
        "Receipt No",
        "Date",
        "Borrower",
        "Phone",
        "Loan ID",
        "Method",
        "Amount",
    ])

    payments = (
        Payment.objects
        .select_related("loan", "loan__borrower")
        .order_by("-payment_date", "-id")
    )

    total = Decimal("0.00")

    for payment in payments:

        ws.append([

            payment.receipt_number,

            payment.payment_date.strftime("%d-%m-%Y"),

            f"{payment.loan.borrower.first_name} {payment.loan.borrower.last_name}",

            payment.loan.borrower.phone,

            payment.loan.id,

            payment.get_method_display(),

            float(payment.amount_paid),

        ])

        total += payment.amount_paid

    ws.append([])

    ws.append([
        "",
        "",
        "",
        "",
        "",
        "TOTAL",
        float(total),
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="Payment_Register.xlsx"'

    wb.save(response)

    return response