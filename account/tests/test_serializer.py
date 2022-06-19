from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase

from account.serializer import UserSerializer
from post.models import Post

UserModel = get_user_model()


class UserSerializerTestCase(TestCase):
    def setUp(self):
        email = 'john.doe@example.com'
        password = '123456super'
        self.user = UserModel.objects.create_user(email, password)

        email2 = 'jane.doe@example.com'
        password2 = '123456super'
        self.user2 = UserModel.objects.create_user(email2, password2)

        Post.objects.bulk_create(
            [Post(title=f'Test title_{i}', text=f'Test text_{i}', owner=self.user) for i in range(1, 4)]
        )
        Post.objects.bulk_create(
            [Post(title=f'Test title_{i}', text=f'Test text_{i}', owner=self.user2) for i in range(1, 6)]
        )

    def test_ok(self):
        users = UserModel.objects.all().annotate(
            posts_count=Count('posts')
        )
        data = UserSerializer(users, many=True).data
        expected_data = [
            {
                'id': self.user.id,
                'email': 'john.doe@example.com',
                'posts_count': 3
            },
            {'id': self.user2.id,
             'email': 'jane.doe@example.com',
             'posts_count': 5
             },
        ]
        self.assertEqual(expected_data, data)
