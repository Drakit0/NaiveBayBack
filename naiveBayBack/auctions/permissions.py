from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuctioneerOrAdmin(BasePermission):
    """
    Allows editing/deleting an auction only if the user is the auctioneer
    or an administrator. Anyone can view (GET).
    """

    def has_object_permission(self, request, view, obj):
        # Allow read access to any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Allow if the user is the auctioneer or an administrator
        return obj.auctioneer == request.user or request.user.is_staff


class IsBidderOrAdmin(BasePermission):
    """
    Allows editing/deleting a bid only if the user is the bidder
    or an administrator. Anyone can view (GET).
    """

    def has_object_permission(self, request, view, obj):
        # Allow read access to any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Allow if the user is the bidder or an administrator
        return obj.bidder == request.user or request.user.is_staff


class IsRaterOrAdmin(BasePermission):
    """
    Allows editing/deleting a rating only if the user is the rater
    or an administrator. Anyone can view (GET).
    """

    def has_object_permission(self, request, view, obj):
        # Allow read access to any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Allow if the user matches the rating user or is an administrator
        return obj.user == request.user or request.user.is_staff

class IsAuthenticatedAuction(BasePermission):
    """
    Allows creating an auction only if the user is authenticated
    or an administrator. Anyone can view (GET).
    """

    def has_permission(self, request, view):
        # Allow read access to any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        
        # Allow if the user is authenticated
        return request.user.is_authenticated
    
class IsAdminCategory(BasePermission):
    """
    Allows editing/deleting a category only if the user is an administrator.
    """
    
    # def has_object_permission(self, request, view, obj):
    #     # Allow read access to any user (GET, HEAD, OPTIONS)
    #     if request.method in SAFE_METHODS:
    #         return True
        
    #     # Allow if the user is an administrator
    #     return request.user.is_staff
    
    def has_permission(self, request, view):
        # Allow read access to any user (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True
        # For methods that create, update, or delete: allow only staff users.
        return request.user.is_staff