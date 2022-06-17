from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import generics, mixins
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from post.models import Post, UserFollowing, UserFeed
from post.serializer import PostSerializer, FollowingSerializer
from post.utils import feed_create_or_add, feed_delete

UserModel = get_user_model()


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)

        try:
            owner = UserModel.objects.get(pk=pk)

        except ObjectDoesNotExist:
            raise NotFound(detail='user not found')

        return Post.objects.filter(owner=owner)


class FollowListCreateAPIView(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                              generics.GenericAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFollowing.objects.filter(user_id=self.request.user)

    def post(self, request, *args, **kwargs):
        feed_create_or_add(self, request)
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            serializer.save(user_id=self.request.user)
        except IntegrityError:
            raise ValidationError({'error': 'You are already follow this user'})

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        feed_delete(self, request)
        return self.destroy(request, *args, **kwargs)


class PostsFeedAPIListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostsFeedListAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostsFeedAPIListPagination

    def get_queryset(self):
        return UserFeed.objects.get(user=self.request.user).feed.all()

    def get(self, request, *args, **kwargs):
        feed_create_or_add(self, request)
        return self.list(request, *args, **kwargs)


class PostFeedRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_feed = UserFeed.objects.get(pk=self.request.user.pk)
        pk = self.kwargs.get('pk')
        try:
            if pk in user_feed.feed.values_list("id", flat=True):
                if pk not in user_feed.read.values_list("id", flat=True):
                    user_feed.read.add(pk)
        except Exception:
            raise NotFound
        return self.retrieve(request, *args, **kwargs)
