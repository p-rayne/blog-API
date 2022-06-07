from django.urls import path

from .views import PostCreateAPIView

urlpatterns = [
    path(r'create/', PostCreateAPIView.as_view(), name='post_create'),
]
