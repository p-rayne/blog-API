from django.urls import path

from .views import PostCreateAPIView, PostListAPIView

urlpatterns = [
    path(r'create/', PostCreateAPIView.as_view(), name='post_create'),
    path(r'posts/<int:pk>/', PostListAPIView.as_view(), name='user_posts'),
]
