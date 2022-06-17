from django.db import models
from rest_framework.exceptions import ValidationError

from blogAPI import settings


class Post(models.Model):
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
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'following_user_id'], name="unique_followers")
        ]

        ordering = ["-created"]

    def clean(self):
        if self.user_id == self.following_user_id:
            raise ValidationError({'error': "Users can't follow themselves"})

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user_id} follows {self.following_user_id}'


class UserFeed(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    feed = models.ManyToManyField(Post, blank=True)
    date_update = models.DateTimeField(auto_now=True)
    read = models.ManyToManyField(Post, blank=True, related_name='readers')

    def __str__(self):
        return f'{self.user} post feed'
