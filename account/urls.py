from django.urls import path
from knox import views as knox_views
from .views import LoginView, UserCreateAPIView

urlpatterns = [
    path(r'login/', LoginView.as_view(), name='knox_login'),
    path(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path(r'user/', UserCreateAPIView.as_view(), name='user_create')
]
