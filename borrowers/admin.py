from django.contrib import admin
from .models import Borrower, Loan, RepaymentSchedule
from .models import Payment
from .models import CompanySettings
from .models import SystemBackup

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'phone',
        'city',
        'state'
    )

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name__in=["Manager", "Loan Officer"]
        ).exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name__in=["Manager", "Loan Officer"]
        ).exists()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name="Manager"
        ).exists()


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'borrower',
        'loan_amount',
        'interest_rate',
        'duration_weeks',
        'status',
        'get_balance'
    )
    actions = [
        'approve_loans',
        'reject_loans',
        'disburse_loans'
    ]
    @admin.action(description="Approve selected loans")
    def approve_loans(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Reject selected loans")
    def reject_loans(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description="Disburse selected loans")
    def disburse_loans(self, request, queryset):
        queryset.update(status='active')

    def get_balance(self, obj):
        return obj.balance()

    get_balance.short_description = "Remaining Balance"

    def has_view_permission(self, request, obj=None):
        return True


    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name__in=["Manager", "Loan Officer"]
        ).exists()


    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name__in=["Manager", "Loan Officer"]
        ).exists()


    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        return request.user.groups.filter(
            name="Manager"
        ).exists()


@admin.register(RepaymentSchedule)
class RepaymentScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'loan',
        'installment_number',
        'amount_due',
        'due_date',
        'status'
    )

    list_filter = ('status',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'loan',
        'amount_paid',
        'payment_date',
        'method'
    )

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "phone",
        "email",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (

        ("Company Information", {
            "fields": (
                "company_name",
                "logo",
                "address",
                "phone",
                "email",
                "website",
            )
        }),

        ("System Settings", {
            "fields": (
                "currency_symbol",
                "receipt_prefix",
                "report_footer",
            )
        }),

        ("Audit", {
            "fields": (
                "updated_at",
            )
        }),

    )

    def has_add_permission(self, request):
        # Only allow one Company Settings record
        return CompanySettings.objects.count() == 0

@admin.register(SystemBackup)
class SystemBackupAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "backup_type",
        "size",
        "created_by",
        "created_at",
    )

    list_filter = (
        "backup_type",
        "created_at",
    )

    search_fields = (
        "filename",
    )