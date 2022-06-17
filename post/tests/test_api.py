import json
from time import sleep

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from post.models import Post, UserFollowing, UserFeed

UserModel = get_user_model()


class PostCreateAPIViewAPITestCase(APITestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

        self.email2 = 'jane.doe@example.com'
        self.password2 = '123456super'
        self.user2 = UserModel.objects.create_user(self.email2, self.password2)

    def test_create_noauth(self):
        self.assertEqual(0, Post.objects.count())
        url = reverse('post_create')
        data = {
            'title': 'Test post title',
            'text': 'Test post text',
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(0, Post.objects.count())

    def test_create(self):
        self.assertEqual(0, Post.objects.count())
        url = reverse('post_create')
        data = {
            'title': 'Test post title',
            'text': 'Test post text',
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Post.objects.count())
        self.assertEqual('john.doe@example.com', Post.objects.last().owner.email)


class PostListAPIViewAPITestCase(APITestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

        self.email2 = 'jane.doe@example.com'
        self.password2 = '123456super'
        self.user2 = UserModel.objects.create_user(self.email2, self.password2)

        for i in range(5):
            Post.objects.create(title=f'Test post title_{i}', text=f'Test post text_{i}', owner=self.user)

        for i in range(2):
            Post.objects.create(title=f'Test post title_{i}', text=f'Test post text_{i}', owner=self.user2)

    def test_user_not_exist(self):
        url = reverse('user_posts', args=(2000,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual({'detail':
                              ErrorDetail(string='user not found',
                                          code='not_found')}, response.data)

    def test_posts_list1(self):
        url = reverse('user_posts', args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, len(response.data))

    def test_posts_list2(self):
        url = reverse('user_posts', args=(self.user2.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))


class FollowListCreateAPIViewAPITestCase(APITestCase):
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

    def test_follow_create(self):
        self.assertEqual(0, UserFollowing.objects.count())
        url = reverse('follow')
        data = {
            'following_user': self.user2.pk
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, UserFollowing.objects.count())

    def test_follow_create_noauth(self):
        self.assertEqual(0, UserFollowing.objects.count())
        url = reverse('follow')
        data = {
            'following_user': self.user2.pk
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(0, UserFollowing.objects.count())

    def test_follow_not_unique(self):
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        url = reverse('follow')
        data = {
            'following_user': self.user2.pk
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_follow_self(self):
        url = reverse('follow')
        data = {
            'following_user': self.user.pk
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_follow_list(self):
        url = reverse('follow')
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_follow_list_noauth(self):
        url = reverse('follow')
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_unfollow(self):
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        UserFeed.objects.create(user=self.user)
        self.assertEqual(1, UserFollowing.objects.count())
        url = reverse('unfollow', args=(UserFollowing.objects.last().pk,))
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(0, UserFollowing.objects.count())

    def test_unfollow_noauth(self):
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        UserFeed.objects.create(user=self.user)
        self.assertEqual(1, UserFollowing.objects.count())
        url = reverse('unfollow', args=(UserFollowing.objects.last().pk,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(1, UserFollowing.objects.count())

    def test_userfeed_create(self):
        self.assertEqual(0, UserFeed.objects.count())
        self.assertFalse(UserFeed.objects.filter(pk=self.user.pk).exists())
        url = reverse('follow')
        data = {
            'following_user': self.user2.pk
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, UserFeed.objects.count())
        self.assertTrue(UserFeed.objects.filter(pk=self.user.pk).exists())
        self.assertIsNotNone(UserFeed.objects.get(pk=self.user.pk).date_update)

    def test_userfeed_update_newfollow(self):
        UserFeed.objects.create(user=self.user)
        self.assertEqual(0, UserFeed.objects.get(pk=self.user.pk).feed.count())
        date = UserFeed.objects.get(pk=self.user.pk).date_update
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        sleep(1)
        Post.objects.create(title='test title', text='test text', owner=self.user2)
        Post.objects.create(title='test2 title', text='test2 text', owner=self.user2)
        sleep(1)
        url = reverse('follow')
        data = {
            'following_user': self.user3.pk
        }
        json_data = json.dumps(data)
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, UserFeed.objects.get(pk=self.user.pk).feed.count())
        self.assertGreater(UserFeed.objects.get(pk=self.user.pk).date_update, date)

    def test_userfeed_update_unfollow(self):
        obj = UserFeed.objects.create(user=self.user)
        self.assertEqual(0, UserFeed.objects.get(pk=self.user.pk).feed.count())
        date = UserFeed.objects.get(pk=self.user.pk).date_update
        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        UserFollowing.objects.create(user=self.user, following_user=self.user3)
        sleep(1)
        obj.feed.create(title='test title', text='test text', owner=self.user2)
        obj.feed.create(title='test2 title', text='test2 text', owner=self.user2)
        self.assertEqual(2, UserFeed.objects.get(pk=self.user.pk).feed.count())
        Post.objects.create(title='test title', text='test text', owner=self.user3)
        self.client.force_authenticate(self.user)
        url = reverse('unfollow', args=(UserFollowing.objects.get(following_user=self.user2.pk).pk,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, UserFeed.objects.get(pk=self.user.pk).feed.count())
        self.assertGreater(UserFeed.objects.get(pk=self.user.pk).date_update, date)


class PostsFeedListAPIViewAPITestCase(APITestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

        self.email2 = 'jane.doe@example.com'
        self.password2 = '123456super'
        self.user2 = UserModel.objects.create_user(self.email2, self.password2)

        UserFollowing.objects.create(user=self.user, following_user=self.user2)
        obj = UserFeed.objects.create(user=self.user)
        for i in range(1, 10):
            obj.feed.create(title=f'Test post title_{i}', text=f'Test post text_{i}', owner=self.user2)

    def test_feed_list_noauth(self):
        url = reverse('posts_feed')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_feed_list(self):
        url = reverse('posts_feed')
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dct = json.loads(response.content)
        self.assertEqual(dct['count'], UserFeed.objects.get(pk=self.user.pk).feed.count())
        a = list(UserFeed.objects.get(pk=self.user.pk).feed.all().values())
        for i in range(len(dct['results'])):
            self.assertEqual(dct['results'][i]['title'], a[i]['title'])

    def test_pagination(self):
        obj = UserFeed.objects.get(user=self.user)
        for i in range(10, 14):
            obj.feed.create(title=f'Test post title_{i}', text=f'Test post text_{i}', owner=self.user2)
        self.assertGreater(obj.feed.count(), 10)
        self.client.force_authenticate(self.user)
        url = reverse('posts_feed')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dct = json.loads(response.content)
        self.assertEqual(dct['count'], obj.feed.count())
        self.assertEqual(10, len(dct['results']))
        self.assertIsNotNone(dct['next'])

    def test_feed_update(self):
        date = UserFeed.objects.get(user=self.user).date_update
        posts = UserFeed.objects.get(user=self.user).feed.count()
        sleep(1)
        Post.objects.create(title='Test title', text='Test text', owner=self.user2)
        self.client.force_authenticate(self.user)
        url = reverse('posts_feed')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual((posts + 1), UserFeed.objects.get(user=self.user).feed.count())
        self.assertGreater(UserFeed.objects.get(user=self.user).date_update, date)
        dct = json.loads(response.content)
        self.assertEqual(dct['results'][0]['title'], UserFeed.objects.get(user=self.user).feed.first().title)
