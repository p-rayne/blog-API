from django.contrib.auth import get_user_model
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

    def test_get(self):
        url = reverse('users')
        response = self.client.get(url)
        serializer_data = UserSerializer([self.user, self.user2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_user(self):
        url = reverse('users')
        data = {'email': 'jax.doe@example.com', 'password': '123456super'}
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, UserModel.objects.count())
        self.assertEqual('jax.doe@example.com', UserModel.objects.latest('date_joined').email)

    def test_email_invalid(self):
        url = reverse('users')
        data = {'email': 'invalid', 'password': '123456super'}
        response = self.client.post(url, data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_password_invalid(self):
        url = reverse('users')
        data = {'email': 'john.doe@example.com', 'password': 12}
        response = self.client.post(url, data)
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
