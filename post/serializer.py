from rest_framework import serializers

from post.models import Post, UserFollowing


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'text',)


class FollowingSerializer(serializers.ModelSerializer):
    following_user = serializers.EmailField(source='following_user_id.email', read_only=True)

    class Meta:
        model = UserFollowing
        fields = ('id', 'following_user', 'following_user_id', 'created', )


class PostsFeedSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'text', 'owner', 'owner_email', 'date_create')
        extra_kwargs = {
            'owner': {'read_only': True},
        }
