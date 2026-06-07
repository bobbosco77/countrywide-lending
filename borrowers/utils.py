from .models import AuditLog


def log_action(user, action, instance, message):

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.id),
        message=message
    )