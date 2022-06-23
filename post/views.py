from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import generics, mixins
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from post.models import Post, UserFollowing, UserFeed
from post.serializer import PostSerializer, FollowingSerializer, UserListSerializer
from post.utils import feed_create_or_add, feed_delete

UserModel = get_user_model()


class UsersListAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    View the list of users and the number of their posts.
    """
    queryset = UserModel.objects.all().only('id', 'email').annotate(
        posts_count=Count('posts')
    )
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]
    filter_backends = (OrderingFilter,)
    ordering_fields = ('posts_count',)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='ordering',
                             description='Sort users by number of posts',
                             required=False,
                             type=str,
                             examples=[
                                 OpenApiExample(
                                     'Example 1',
                                     summary='None',
                                     description='not sorted',
                                 ),
                                 OpenApiExample(
                                     'Example 2',
                                     summary='ascending',
                                     description='Sort by number of posts in ascending order',
                                     value='posts_count'
                                 ),
                                 OpenApiExample(
                                     'Example 3',
                                     summary='descending',
                                     description='Sort by number of posts in descending order',
                                     value='-posts_count'
                                 ),
                             ],
                             ),
        ],
    )
    def get(self, request, *args, **kwargs):
        """
        View the list of users and the number of their posts.
        """
        return self.list(request, *args, **kwargs)


class PostCreateAPIView(generics.CreateAPIView):
    """
    Allows the user to create new posts.
    Requires authentication.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostListAPIView(generics.ListAPIView):
    """
    Allows you to view a list of other users posts.
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if UserModel.objects.filter(pk=pk).exists():
            return Post.objects.filter(owner_id=pk).select_related('owner')
        else:
            raise NotFound({'error': 'User not found'})


class FollowListCreateAPIView(mixins.CreateModelMixin, mixins.ListModelMixin,
                              generics.GenericAPIView):
    """
    Allows you to subscribe to users, view the list of subscriptions.
    Requires authentication.
    """
    serializer_class = FollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFollowing.objects.filter(user=self.request.user). \
            select_related('following_user'). \
            only('following_user__id', 'following_user__email', 'created')

    def post(self, request, *args, **kwargs):
        """
        Subscribe to user.
        """
        feed_create_or_add(self)
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({'error': 'You are already follow this user'})

    def get(self, request, *args, **kwargs):
        """
        View the list of subscriptions.
        """
        return self.list(request, *args, **kwargs)


@extend_schema_view(delete=extend_schema(responses=None))
class UnfollowAPIView(mixins.DestroyModelMixin, generics.GenericAPIView):
    """
    Allows you to unsubscribe to users.
    In order to unsubscribe from a user, you must pass his id in the request.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):

        try:
            feed_delete(self)
            return self.destroy(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise NotFound({'error': 'You are not following the user with this id'})

    def get_object(self):
        following_user = self.kwargs.get('following_user')
        return UserFollowing.objects.get(user=self.request.user, following_user=following_user)


class PostsFeedAPIListPagination(PageNumberPagination):
    """
    Page pagination. The default is 10 posts per page.
    You can change the number of posts by passing the 'page_size' parameter.
    Max value = 100 posts per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostsFeedListAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    Allows you to view the feed of posts.
    You can filter the feed using the 'readed' parameter:
        ?readed=true will display only read posts from the feed.
        ?readed=false will only display unread posts from the feed.
        if the parameter is not passed in the request, then all posts will be displayed.
    Requires authentication.
    """
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostsFeedAPIListPagination

    def get_queryset(self):
        readed = self.request.query_params.get('readed')
        obj = UserFeed.objects.get(user=self.request.user)
        if readed is None:
            queryset = obj.feed.all().select_related('owner'). \
                only('id', 'title', 'text', 'date_create', 'owner__id', 'owner__email')
            return queryset
        elif readed == 'true':
            queryset = obj.read.all().select_related('owner'). \
                only('id', 'title', 'text', 'date_create', 'owner__id', 'owner__email')
            return queryset
        elif readed == 'false':
            queryset = obj.feed.exclude(id__in=obj.read.all()).select_related('owner'). \
                only('id', 'title', 'text', 'date_create', 'owner__id', 'owner__email')
            return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name='readed',
                             description='Filtering already read posts',
                             required=False,
                             type=str,
                             examples=[
                                 OpenApiExample(
                                     'Example 1',
                                     summary='None',
                                     description='All posts are displayed',
                                 ),
                                 OpenApiExample(
                                     'Example 2',
                                     summary='Already read',
                                     description='Only posts that have been read are displayed',
                                     value='true'
                                 ),
                                 OpenApiExample(
                                     'Example 3',
                                     summary='Unread',
                                     description='Only unread posts are displayed',
                                     value='false'
                                 ),
                             ],
                             ),
        ],
    )
    def get(self, request, *args, **kwargs):
        feed_create_or_add(self)
        return self.list(request, *args, **kwargs)


class PostFeedRetrieveAPIView(generics.RetrieveAPIView):
    """
    Allows you to add posts to the "read" field of the feed.
    If the post has already been added, displays information about the post.
    Requires authentication.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_feed = UserFeed.objects.get(pk=self.request.user.pk)
        pk = self.kwargs.get('pk')
        if pk in user_feed.feed.values_list("id", flat=True):
            if pk not in user_feed.read.values_list("id", flat=True):
                user_feed.read.add(pk)
        else:
            raise NotFound({'error': 'Post not found in your feed'})
        return self.retrieve(request, *args, **kwargs)
