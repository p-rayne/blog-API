import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from post.models import Post

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
