from django.db.models import F
from django.utils.deprecation import MiddlewareMixin

from coin.models import History


class TotalVisitsMiddleware(MiddlewareMixin):
    """Increements overall total site visits by +1 each time a user visits 
    Leading Wealth."""

    def process_request(self, request):
        History.objects.filter(pk=1).update(
            total_visits=F('total_visits')+1
        )