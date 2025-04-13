from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsNotRegistered(BasePermission):
    """
    Permite el registro solo a usuarios no autenticados.
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated