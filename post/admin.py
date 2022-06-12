from django.contrib import admin
from django.contrib.admin import ModelAdmin

from post.models import Post, UserFollowing


@admin.register(Post)
class PostAdmin(ModelAdmin):
    pass


@admin.register(UserFollowing)
class PostAdmin(ModelAdmin):
    pass
