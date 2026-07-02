from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),

    path('register/', views.register_borrower, name='register'),
    path('loan/', views.create_loan, name='loan_form'),

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
]