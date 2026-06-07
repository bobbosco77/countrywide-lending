from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Loan, RepaymentSchedule
from .models import Payment, RepaymentSchedule
from datetime import date, timedelta

@receiver(post_save, sender=Loan)
def create_repayment_schedule(sender, instance, created, **kwargs):
    if created:
        monthly = instance.monthly_payment()

        for i in range(1, instance.duration_months + 1):
            RepaymentSchedule.objects.create(
                loan=instance,
                installment_number=i,
                due_date=date.today() + timedelta(days=30 * i),
                amount_due=monthly
            )

@receiver(post_save, sender=Payment)
def allocate_payment(sender, instance, created, **kwargs):

    if not created:
        return

    unpaid = RepaymentSchedule.objects.filter(
        loan=instance.loan,
        status='pending'
    ).order_by('installment_number')

    remaining_amount = instance.amount_paid

    for installment in unpaid:

        if remaining_amount >= installment.amount_due:

            installment.status = 'paid'
            installment.save()

            remaining_amount -= installment.amount_due

        else:
            break

    loan = instance.loan

    if loan.balance() <= 0:
        loan.status = 'closed'
        loan.save()