from post.models import UserFollowing, Post, UserFeed


def feed_create_or_add(self, request):
    user = self.request.user

    obj, created = UserFeed.objects.get_or_create(user=user)

    following_id = UserFollowing.objects.filter(user_id=user).values_list('following_user_id', flat=True)
    posts = Post.objects.filter(owner__in=following_id,
                                date_create__gte=obj.date_update).values_list('pk', flat=True)
    obj.feed.add(*posts)
    obj.save()
