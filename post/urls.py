from django.urls import path

from .views import PostCreateAPIView, PostListAPIView, FollowListCreateAPIView

urlpatterns = [
    path(r'create/', PostCreateAPIView.as_view(), name='post_create'),
    path(r'posts/<int:pk>/', PostListAPIView.as_view(), name='user_posts'),
    path(r'follow/', FollowListCreateAPIView.as_view(), name='follow'),
    path(r'follow/<int:pk>/', FollowListCreateAPIView.as_view(), name='unfollow'),
]
