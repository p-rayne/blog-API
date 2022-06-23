from django.contrib.auth import get_user_model, login
from django.db.models import Count
from rest_framework import generics, mixins
from knox.views import LoginView as KnoxLoginView
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from .scheme import KnoxTokenScheme
from account.serializer import UserSerializer, CustomAuthTokenSerializer

UserModel = get_user_model()


class UserListCreateAPIView(mixins.CreateModelMixin, mixins.ListModelMixin,
                            generics.GenericAPIView):
    """
    Allows you to create a new user, view the list of users and the number of their posts.
    """
    queryset = UserModel.objects.all().only('id', 'email').annotate(
        posts_count=Count('posts')
    )
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = (OrderingFilter,)
    ordering_fields = ('posts_count',)

    def get(self, request, *args, **kwargs):
        """
        View the list of users and the number of their posts.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new user.
        """
        return self.create(request, *args, **kwargs)


class LoginView(KnoxLoginView):
    """
    User authentication. After successful validation, the user receives a token.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, format=None):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)
