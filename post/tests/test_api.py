import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from post.models import Post

UserModel = get_user_model()


class PostCreateAPIViewTestCase(APITestCase):
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
