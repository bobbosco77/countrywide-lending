from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, RepaymentSchedule


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

        installment_balance = (
            installment.amount_due - installment.amount_paid
        )

        # Installment can be fully settled
        if remaining_amount >= installment_balance:

            installment.amount_paid += installment_balance
            installment.status = 'paid'
            installment.save()

            remaining_amount -= installment_balance

        # Partial payment
        else:

            installment.amount_paid += remaining_amount
            installment.save()

            remaining_amount = 0
            break

    loan = instance.loan

    # Close the loan only when every installment is paid
    if not RepaymentSchedule.objects.filter(
        loan=loan,
        status='pending'
    ).exists():

        loan.status = 'closed'
        loan.save()