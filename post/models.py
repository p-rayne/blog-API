from django.db import models

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
