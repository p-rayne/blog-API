from post.models import UserFollowing, Post, UserFeed


def feed_create_or_add(self, request):
    user = self.request.user

    obj, created = UserFeed.objects.get_or_create(user=user)

    following_id = user.following.values_list('following_user', flat=True)
    posts = Post.objects.filter(owner__in=following_id,
                                date_create__gte=obj.date_update).values_list('pk', flat=True)
    obj.feed.add(*posts)
    obj.save()


def feed_delete(self, request):
    user = self.request.user
    following_user = self.kwargs.get('following_user')

    obj = UserFeed.objects.get(user=user)

    following_id = user.following.exclude(following_user=following_user).values_list('following_user', flat=True)
    posts = Post.objects.filter(owner__in=following_id,
                                date_create__gte=obj.date_update).values_list('pk', flat=True)
    obj.feed.add(*posts)
    unfollow_post = obj.feed.filter(owner_id=following_user)
    obj.feed.remove(*unfollow_post)
    obj.save()
