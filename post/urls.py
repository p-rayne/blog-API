from django.urls import path

from .views import PostCreateAPIView, PostListAPIView, FollowListCreateAPIView, PostsFeedListAPIView, \
    PostFeedRetrieveAPIView

urlpatterns = [
    path(r'create/', PostCreateAPIView.as_view(), name='post_create'),
    path(r'posts/<int:pk>/', PostListAPIView.as_view(), name='user_posts'),
    path(r'follow/', FollowListCreateAPIView.as_view(), name='follow'),
    path(r'follow/<int:following_user>/', FollowListCreateAPIView.as_view(), name='unfollow'),
    path(r'posts/feed/', PostsFeedListAPIView.as_view(), name='posts_feed'),
    path(r'posts/feed/<int:pk>/', PostFeedRetrieveAPIView.as_view(), name='post_read'),
]
