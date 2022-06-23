import json

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse
from knox.models import AuthToken
from rest_framework import status
from rest_framework.test import APITestCase

from account.serializer import UserSerializer

UserModel = get_user_model()


class UserListCreateAPITestCase(APITestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

        self.email2 = 'jane.doe@example.com'
        self.password2 = '123456super'
        self.user2 = UserModel.objects.create_user(self.email2, self.password2)

    def test_create_user(self):
        url = reverse('user_create')
        data = {'email': 'jax.doe@example.com', 'password': '123456super'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, UserModel.objects.count())
        self.assertEqual('jax.doe@example.com', UserModel.objects.last().email)

    def test_email_invalid(self):
        url = reverse('user_create')
        data = {'email': 'invalid', 'password': '123456super'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_email_empty(self):
        url = reverse('user_create')
        data = {'email': '', 'password': '123456super'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_password_short(self):
        url = reverse('user_create')
        data = {'email': 'john.doe@example.com', 'password': 'abc12'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_password_empty(self):
        url = reverse('user_create')
        data = {'email': 'john.doe@example.com', 'password': ''}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_password_numeric_only(self):
        url = reverse('user_create')
        data = {'email': 'john.doe@example.com', 'password': 123456789}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class LoginViewAPITestCase(APITestCase):
    def setUp(self):
        self.email = 'john.doe@example.com'
        self.password = '123456super'
        self.user = UserModel.objects.create_user(self.email, self.password)

    def test_login_creates_keys(self):
        self.assertEqual(0, AuthToken.objects.count())
        url = reverse('knox_login')

        for _ in range(5):
            self.client.post(url, {'email': 'john.doe@example.com', 'password': '123456super'}, format='json')
        self.assertEqual(5, AuthToken.objects.count())
        self.assertTrue(all(e.token_key for e in AuthToken.objects.all()))

    def test_login_returns_serialized_token(self):
        self.assertEqual(0, AuthToken.objects.count())
        url = reverse('knox_login')
        response = self.client.post(url, {'email': 'john.doe@example.com', 'password': '123456super'}, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIn('token', response.data)
        username_field = self.user.USERNAME_FIELD
        self.assertNotIn(username_field, response.data)
