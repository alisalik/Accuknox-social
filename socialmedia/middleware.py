from django.utils import timezone
from django.http import HttpResponseBadRequest
from datetime import timedelta
from .models import FriendRequest
from django.utils.deprecation import MiddlewareMixin


class FriendRequestLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.method == 'POST' and request.path == '/api/v1/send_requests/':
            current_user = request.user
            
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_requests_count = FriendRequest.objects.filter(from_user=current_user, created_at__gte=one_minute_ago).count()
            if recent_requests_count >= 3:
                return HttpResponseBadRequest("You cannot send more than 3 friend requests within a minute.")
        
        return response
