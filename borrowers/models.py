from django.db import models
from decimal import Decimal
from datetime import date, timedelta
from django.contrib.auth.models import User

class Borrower(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    occupation = models.CharField(max_length=100)

    next_of_kin_name = models.CharField(max_length=100)
    next_of_kin_phone = models.CharField(max_length=20)

    nin = models.CharField(max_length=50)
    bvn = models.CharField(max_length=50)

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)

    guarantor_name = models.CharField(max_length=100)
    guarantor_address = models.TextField()
    guarantor_phone = models.CharField(max_length=20)
    guarantor_occupation = models.CharField(max_length=100)

    borrower_photo = models.ImageField(upload_to='borrowers/')
    guarantor_photo = models.ImageField(upload_to='guarantors/')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + " " + self.last_name
    


class Loan(models.Model):
    borrower = models.ForeignKey(
        'Borrower',
        on_delete=models.CASCADE,
        related_name='loans'
    )

    loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    duration_weeks = models.PositiveIntegerField()

    start_date = models.DateField(
        auto_now_add=True
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        ordering = ['-start_date']

    def total_repayment(self):
        """
        Total amount borrower is expected to repay.
        Formula currently assumes interest_rate is weekly.
        """
        interest = (
            self.loan_amount *
            self.interest_rate *
            self.duration_weeks
        ) / Decimal('100')

        return self.loan_amount + interest

    def weekly_payment(self):
        """
        weekly installment amount.
        """
        if self.duration_weeks <= 0:
            return Decimal('0.00')

        return self.total_repayment() / Decimal(self.duration_weeks)

    @property
    def total_paid(self):
        """
        Sum of all payments received for this loan.
        """
        total = self.payments.aggregate(
            total=models.Sum('amount_paid')
        )['total']

        return total or Decimal('0.00')

    @property
    def balance(self):
        """
        Outstanding loan balance.
        """
        return self.total_repayment() - self.total_paid

    def generate_repayment_schedule(self):

        if RepaymentSchedule.objects.filter(loan=self).exists():
            return

        weekly_amount = self.weekly_payment()

        for installment in range(1, self.duration_weeks + 1):
            RepaymentSchedule.objects.create(
                loan=self,
                installment_number=installment,
                due_date=date.today() + timedelta(weeks=installment),
                amount_due=weekly_amount,
                status='pending'
            )

    def __str__(self):
        return f"{self.borrower.first_name} {self.borrower.last_name} - ₦{self.loan_amount}"

class RepaymentSchedule(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    installment_number = models.IntegerField()

    due_date = models.DateField()

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    @property
    def balance(self):
        return self.amount_due - self.amount_paid

    def save(self, *args, **kwargs):

        if self.amount_paid >= self.amount_due:
            self.amount_paid = self.amount_due
            self.status = 'paid'

        elif self.amount_paid > 0:
            self.status = 'partial'

        else:
            self.status = 'pending'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan.id} - Week {self.installment_number}"    
class Payment(models.Model):

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateField(
        auto_now_add=True
    )

    PAYMENT_METHOD = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
    ]

    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default='cash'
    )

    def __str__(self):
        return f"{self.loan.borrower.first_name} - {self.amount_paid}"

    @property
    def receipt_number(self):
        return f"CW-{self.payment_date.strftime('%Y%m%d')}-{self.id:06d}"

class AuditLog(models.Model):

    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('PAYMENT', 'Payment'),
        ('LOAN', 'Loan Action'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)

    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, null=True, blank=True)

    message = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"
    

from django.db import models


class CompanySettings(models.Model):
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="company/", blank=True, null=True)

    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    currency_symbol = models.CharField(
        max_length=10,
        default="₦"
    )

    receipt_prefix = models.CharField(
        max_length=20,
        default="CWLS"
    )

    report_footer = models.TextField(
        default="Thank you for choosing CountryWide Lending & Services."
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return self.company_name