from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),

    path('register/', views.register_borrower, name='register'),

    path(
        'borrower/<int:borrower_id>/',
        views.borrower_profile,
        name='borrower_profile'
    ),

    path(
        'borrowers/',
        views.borrower_list,
        name='borrower_list'
    ),

    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'defaulters/',
        views.defaulters_report,
        name='defaulters_report'
    ),
    path(
        'loan/', 
        views.create_loan, 
        name='loan_form'
    ),
    path(
        'loans/',
        views.loan_register,
        name='loan_register'
    ),

    path(
        'loans/pdf/',
        views.loan_register_pdf,
        name='loan_register_pdf'
    ),

    path(
        'loans/excel/',
        views.loan_register_excel,
        name='loan_register_excel'
    ),
    path(
        'loan/<int:loan_id>/',
        views.loan_detail,
        name='loan_detail'
    ),

    path(
        'loan/<int:loan_id>/pdf/',
        views.loan_statement_pdf,
        name='loan_pdf'
    ),
    path(
        'borrowers/pdf/',
        views.borrowers_pdf,
        name='borrowers_pdf'
    ),
    path(
        "payments/register/",
        views.payment_register,
        name="payment_register",
    ),
    path(
        "payments/register/pdf/",
        views.payment_register_pdf,
        name="payment_register_pdf",
    ),

    path(
        "payments/register/excel/",
        views.payment_register_excel,
        name="payment_register_excel",
    ),

    path(
        'payment/',
        views.make_payment,
        name='make_payment'
    ),
    path(
        'payment/<int:payment_id>/receipt/',
        views.payment_receipt,
        name='payment_receipt'
    ),
    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),
    path(
        'defaulters/export/excel/',
        views.export_defaulters_excel,
        name='export_defaulters_excel'
    ),
    path(
        'defaulters/export/pdf/',
        views.export_defaulters_pdf,
        name='export_defaulters_pdf'
    ),
    path(
    "reports/loans/",
    views.all_loans_report,
        name="all_loans_report",
    ),

    path(
        "reports/payments/",
        views.all_payments_report,
        name="all_payments_report",
    ),
    path(
    "reports/loans/pdf/",
    views.export_loans_pdf,
    name="export_loans_pdf",
    ),

    path(
        "reports/payments/pdf/",
        views.export_payments_pdf,
        name="export_payments_pdf",
    ),

    path(
        "reports/loans/excel/",
        views.export_loans_excel,
        name="export_loans_excel",
    ),

    path(
        "reports/payments/excel/",
        views.export_payments_excel,
        name="export_payments_excel",
    ),
]