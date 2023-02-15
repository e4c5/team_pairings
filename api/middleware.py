from django.http import Http404

from tournament.models import Tournament

class TournamentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        path = request.get_full_path()
        parts = path.split('/api/tournament/')
        if len(parts) == 2:
            parts = parts[1].split('/')
            if parts[0]:
                try:
                    request.tournament = Tournament.objects.get(pk=parts[0])
                except Tournament.DoesNotExist:
                    raise Http404('Tournament not found')
            
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response