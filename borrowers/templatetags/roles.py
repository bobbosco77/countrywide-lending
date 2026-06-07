from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()

@register.filter
def is_cashier(user):
    return user.groups.filter(name='Cashier').exists()

@register.filter
def is_loan_officer(user):
    return user.groups.filter(name='Loan Officer').exists()

@register.filter
def is_auditor(user):
    return user.groups.filter(name='Auditor').exists()