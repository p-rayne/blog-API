from django.contrib.auth import get_user_model
from rest_framework import serializers

from post.models import Post, UserFollowing

UserModel = get_user_model()


class PostOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'email')


class PostSerializer(serializers.ModelSerializer):
    owner = PostOwnerSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'owner', 'date_create',)


class FollowingSerializer(serializers.ModelSerializer):
    follow_to = PostOwnerSerializer(read_only=True, source='following_user')

    class Meta:
        model = UserFollowing
        fields = ('follow_to', 'following_user', 'created')
        extra_kwargs = {
            'following_user': {'write_only': True},
        }
