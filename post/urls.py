from django.urls import path

from .views import PostCreateAPIView, PostListAPIView, FollowListCreateAPIView, PostsFeedListAPIView, \
    PostFeedRetrieveAPIView, UnfollowAPIView, UsersListAPIView

urlpatterns = [
    path(r'users/', UsersListAPIView.as_view(), name='users_list'),
    path(r'posts/<int:pk>/', PostListAPIView.as_view(), name='user_posts'),
    path(r'create/', PostCreateAPIView.as_view(), name='post_create'),
    path(r'follow/', FollowListCreateAPIView.as_view(), name='follow'),
    path(r'unfollow/<int:following_user>/', UnfollowAPIView.as_view(), name='unfollow'),
    path(r'feed/', PostsFeedListAPIView.as_view(), name='posts_feed'),
    path(r'feed/<int:pk>/', PostFeedRetrieveAPIView.as_view(), name='post_read'),
]
