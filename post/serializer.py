from rest_framework import serializers

from post.models import Post, UserFollowing


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'text',)


class FollowingSerializer(serializers.ModelSerializer):
    following_user = serializers.EmailField(source='following_user_id.email')

    class Meta:
        model = UserFollowing
        fields = ('id', 'following_user', 'following_user_id', 'created', )


# class FollowersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserFollowing
#         fields = ("id", "user_id", "created")
