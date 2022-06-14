from django.contrib import admin
from django.contrib.admin import ModelAdmin

from post.models import Post, UserFollowing, UserFeed


@admin.register(Post)
class PostAdmin(ModelAdmin):
    pass


@admin.register(UserFollowing)
class PostAdmin(ModelAdmin):
    pass


@admin.register(UserFeed)
class PostAdmin(ModelAdmin):
    pass
