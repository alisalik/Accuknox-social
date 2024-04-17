from django.urls import path
from .views import UsersAPIView,CustomTokenRefreshView,UserSearchAPIView,Requests
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'auth/signup', UsersAPIView, basename="user-signup")
router.register('send_requests',Requests,basename='requests')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/',include([
    path('login/',UsersAPIView.as_view({'post':'login'}),name='login'),
    path('action_request/',Requests.as_view({'post':'action_request'}),name='request_action'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('search/', UserSearchAPIView.as_view(), name='user-search'),
    path('logout/',UsersAPIView.as_view({'post':'logout'}),name='logout')]))
]