from post.models import Post, UserFeed


def feed_create_or_add(self):
    """
    Creates or updates a user's post feed.
    Adds 'following_user' posts created after 'date_update'.
    Once added, updates the 'date_update' field.
    """
    user = self.request.user
    obj, created = UserFeed.objects.get_or_create(user=user)
    following_id = user.following.values_list('following_user', flat=True)
    posts = Post.objects.filter(owner__in=following_id,
                                date_create__gte=obj.date_update).values_list('pk', flat=True)
    obj.feed.add(*posts)
    obj.save()


def feed_delete(self):
    """
    When unsubscribing from a user, removes his posts from the "feed" and "read" fields of the feed.
    Does NOT update the "date update" field.
    """
    user = self.request.user
    following_user = self.kwargs.get('following_user')
    obj = UserFeed.objects.get(user=user)
    unfollow_post_feed = obj.feed.filter(owner_id=following_user).values_list('id', flat=True)
    unfollow_post_read = obj.read.filter(owner_id=following_user).values_list('id', flat=True)
    obj.feed.remove(*unfollow_post_feed)
    obj.read.remove(*unfollow_post_read)
