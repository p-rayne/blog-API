from django.contrib.auth import get_user_model, login
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import generics, mixins
from knox.views import LoginView as KnoxLoginView
from rest_framework.permissions import AllowAny

from blogAPI.schema import KnoxTokenScheme
from account.serializer import UserSerializer, CustomAuthTokenSerializer

UserModel = get_user_model()


class UserCreateAPIView(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Allows you to create a new user.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        responses={201: UserSerializer},
    )
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
