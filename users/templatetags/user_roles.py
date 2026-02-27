from django import template

from users.models import UserRole

register = template.Library()


@register.filter(name="is_admin")
def is_admin(user):
    """
    Returns True when the user has an administrative role.
    Works with authenticated users only; anonymous users always return False.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    return getattr(user, "role", None) in (UserRole.ADMIN, UserRole.ADMIN_STAFF)
