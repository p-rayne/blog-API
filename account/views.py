from django.contrib.auth import get_user_model, login
from django.db.models import Count
from rest_framework import generics, permissions
from knox.views import LoginView as KnoxLoginView
from rest_framework.filters import OrderingFilter

from account.serializer import UserSerializer, CustomAuthTokenSerializer

UserModel = get_user_model()


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = UserModel.objects.all().only('id', 'email').annotate(
        posts_count=Count('posts')
    )
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (OrderingFilter,)
    ordering_fields = ('posts_count',)


class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)
