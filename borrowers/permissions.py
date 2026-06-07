from django.core.exceptions import PermissionDenied

# ========================
# ROLE ENGINE
# ========================

def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()


def is_cashier(user):
    return user.is_superuser or user.groups.filter(name='Cashier').exists()


def is_loan_officer(user):
    return user.is_superuser or user.groups.filter(name='Loan Officer').exists()


def is_auditor(user):
    return user.is_superuser or user.groups.filter(name='Auditor').exists()


def has_role(user, roles):
    return user.is_superuser or user.groups.filter(name__in=roles).exists()


# ========================
# DECORATORS
# ========================

def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not has_role(request.user, roles):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator