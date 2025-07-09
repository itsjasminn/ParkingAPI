from rest_framework.permissions import BasePermission

from user.models import User


class IsAdmin(BasePermission):
    message = 'Sen admin roleda emmasan !'

    def has_permission(self, request, view):
        return request.user.role == User.RoleType.ADMIN.value
