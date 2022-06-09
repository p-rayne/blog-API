from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny

from post.models import Post
from post.serializer import PostCreateSerializer

UserModel = get_user_model()


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)

        try:
            owner = UserModel.objects.get(pk=pk)

        except ObjectDoesNotExist:
            raise NotFound(detail='user not found')

        return Post.objects.filter(owner=owner)
