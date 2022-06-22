from django.contrib import admin

from post.models import Post, UserFollowing, UserFeed


class PostAdmin(admin.ModelAdmin):
    """
    Manage User posts.
    """
    list_display = ('id', 'title', 'owner', 'date_create')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'text', 'owner')
    list_filter = ('date_create',)


class UserFollowingAdmin(admin.ModelAdmin):
    """
    Manage User subscriptions.
    """
    list_display = ('id', 'user', 'following_user', 'created')
    list_display_links = ('id', 'user')
    search_fields = ('user', 'following_user')
    list_filter = ('created',)


class UserFeedAdmin(admin.ModelAdmin):
    """
    User feed management.
    """
    list_display = ('user', 'date_update')
    list_display_links = ('user',)
    search_fields = ('user',)
    list_filter = ('date_update',)


admin.site.register(Post, PostAdmin)
admin.site.register(UserFollowing, UserFollowingAdmin)
admin.site.register(UserFeed, UserFeedAdmin)
