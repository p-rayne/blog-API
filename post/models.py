from django.db import models
from rest_framework.exceptions import ValidationError

from blogAPI import settings


class Post(models.Model):
    """
    User post model.
    """
    title = models.CharField(max_length=255)
    text = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts')
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_create']


class UserFollowing(models.Model):
    """
    User subscription model. Does not allow you to follow yourself or follow the same user twice.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
    following_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'following_user'], name="unique_followers")
        ]

        ordering = ["-created"]

    def clean(self):
        if self.user == self.following_user:
            raise ValidationError({'error': "Users can't follow themselves"})

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} follows {self.following_user}'


class UserFeed(models.Model):
    """
    User's post feed model.
    User posts are added to the 'feed' field after subscribing to them.
    (Posts created before the moment of subscription will not be added.)
    The 'read' field contains the id of posts that have been read.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    feed = models.ManyToManyField(Post, blank=True)
    date_update = models.DateTimeField(auto_now=True)
    read = models.ManyToManyField(Post, blank=True, related_name='readers')

    def __str__(self):
        return f'{self.user} post feed'
