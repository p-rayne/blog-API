import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from post.models import Post
from post.serializer import PostOwnerSerializer, PostSerializer

UserModel = get_user_model()


class PostOwnerSerializerTestCase(TestCase):
    def setUp(self):
        email = 'john.doe@example.com'
        password = '123456super'
        self.user = UserModel.objects.create_user(email, password)

        email2 = 'jane.doe@example.com'
        password2 = '123456super'
        self.user2 = UserModel.objects.create_user(email2, password2)

    def test_owner_ok(self):
        users = UserModel.objects.all()
        data = PostOwnerSerializer(users, many=True).data
        expected_data = [
            {
                'id': self.user.id,
                'email': 'john.doe@example.com',
            },
            {
                'id': self.user2.id,
                'email': 'jane.doe@example.com',
            },
        ]
        self.assertEqual(expected_data, data)


class PostSerializerTestCase(TestCase):
    def setUp(self):
        email = 'john.doe@example.com'
        password = '123456super'
        self.user = UserModel.objects.create_user(email, password)

        email2 = 'jane.doe@example.com'
        password2 = '123456super'
        self.user2 = UserModel.objects.create_user(email2, password2)

        self.user.posts.create(title='Test title', text='Test text')
        self.user2.posts.create(title='Test title2', text='Test text2')

    def test_posts_ok(self):
        posts = Post.objects.all()
        data = PostSerializer(posts, many=True).data
        date = Post.objects.get(owner=self.user).date_create.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        date2 = Post.objects.get(owner=self.user2).date_create.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        expected_data = [
            {
                "id": Post.objects.get(owner=self.user2).id,
                "title": "Test title2",
                "text": "Test text2",
                "owner": {
                    "id": self.user2.pk,
                    "email": "jane.doe@example.com"
                },
                "date_create": date2
            },
            {
                'id': Post.objects.get(owner=self.user).id,
                'title': 'Test title',
                'text': 'Test text',
                'owner': {
                    "id": self.user.pk,
                    "email": "john.doe@example.com"
                },
                'date_create': date
            },
        ]
        self.assertEqual(expected_data, data)
