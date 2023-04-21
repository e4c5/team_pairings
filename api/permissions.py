from rest_framework.permissions import BasePermission, SAFE_METHODS
from tournament.models import Tournament

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if request.user and request.user.is_authenticated:
            if hasattr(request, 'tournament'):
                td = request.tournament.director_set.filter(user=request.user)
                if td.exists():
                    return True
            return request.get_full_path() == '/api/tournament/' and request.method == 'POST'
        return False                        






