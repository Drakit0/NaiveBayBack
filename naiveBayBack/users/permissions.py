from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsNotRegistered(BasePermission):
    """
    Allows registration only for unauthenticated users.
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated
    
class IsOwnerOrAdmin(BasePermission):
    """
    Allows editing/deleting a user only if the user is the owner
    or an administrator. Anyone can view (GET).
    """
    def has_object_permission(self, request, view, obj):
        
        # Permitir si el usuario es el propietario o es administrador
        return obj == request.user or request.user.is_staff