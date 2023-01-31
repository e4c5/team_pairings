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
            tid =  view.kwargs.get('tid')
            if tid:
                if Tournament.objects.filter(pk=tid).filter(director__user=request.user).exists():
                    return True
            else:
                pk = view.kwargs.get('pk')
                if pk:
                    if Tournament.objects.filter(pk=pk).exists():
                        return True

        return False                        






