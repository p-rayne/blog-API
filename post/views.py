from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from post.serializer import PostCreateSerializer


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
