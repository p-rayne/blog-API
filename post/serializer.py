from django.contrib.auth import get_user_model
from rest_framework import serializers

from post.models import Post, UserFollowing

UserModel = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """
    Displays information about the user, and also shows the number of his posts.
    """
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserModel
        fields = (
            'id', 'email', 'posts_count',
        )


class PostOwnerSerializer(serializers.ModelSerializer):
    """
    Displays the "id" and "email" of the requested user.
    """

    class Meta:
        model = UserModel
        fields = ('id', 'email')


class PostSerializer(serializers.ModelSerializer):
    """
    Displays information about the post and its owner.
    """
    owner = PostOwnerSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'owner', 'date_create',)


class FollowingSerializer(serializers.ModelSerializer):
    """
    Displays information about the subscribed user and date of subscription.
    """
    follow_to = PostOwnerSerializer(read_only=True, source='following_user')

    class Meta:
        model = UserFollowing
        fields = ('follow_to', 'following_user', 'created')
        extra_kwargs = {
            'following_user': {'write_only': True},
        }
