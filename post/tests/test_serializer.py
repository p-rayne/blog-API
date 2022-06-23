from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase

from post.models import Post, UserFollowing
from post.serializer import PostOwnerSerializer, PostSerializer, FollowingSerializer, UserListSerializer

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


class FollowingSerializerTestCase(TestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

        self.email2 = 'jane.doe@example.com'
        self.password2 = '123456super'
        self.user2 = UserModel.objects.create_user(self.email2, self.password2)

        self.email3 = 'jax.doe@example.com'
        self.password3 = '123456super'
        self.user3 = UserModel.objects.create_user(self.email3, self.password3)

        self.user.following.create(following_user=self.user2)
        self.user.following.create(following_user=self.user3)

    def test_follows_ok(self):
        follows = UserFollowing.objects.all()
        data = FollowingSerializer(follows, many=True).data
        date1 = UserFollowing.objects.get(following_user=self.user2).created.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        date2 = UserFollowing.objects.get(following_user=self.user3).created.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        expected_data = [
            {
                "follow_to": {
                    "id": self.user3.pk,
                    "email": "jax.doe@example.com"
                },
                "created": date2
            },
            {
                "follow_to": {
                    "id": self.user2.pk,
                    "email": "jane.doe@example.com"
                },
                "created": date1
            }
        ]
        self.assertEqual(expected_data, data)


class UserListSerializerTestCase(TestCase):
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

    def test_UserList_ok(self):
        users = UserModel.objects.all().annotate(
            posts_count=Count('posts')
        )
        data = UserListSerializer(users, many=True).data
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
