from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.serializer import UserSerializer

UserModel = get_user_model()


class UserListCreateAPITestCase(APITestCase):
    def setUp(self):
        self.user_1 = UserModel.objects.create(email='test', password=12)
        self.user_2 = UserModel.objects.create(email='test@test.com', password='123456super')

    def test_get(self):
        url = reverse('users')
        response = self.client.get(url)
        serializer_data = UserSerializer([self.user_1, self.user_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create_user(self):
        url = reverse('users')
        data = {'email': 'test@create.com', 'password': '123456super'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, UserModel.objects.count())
        self.assertEqual('test@create.com', UserModel.objects.latest('date_joined').email)

    def test_email_invalid(self):
        url = reverse('users')
        data = {'email': 'test', 'password': '123456super'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_password_invalid(self):
        url = reverse('users')
        data = {'email': 'test', 'password': 12}
        response = self.client.post(url, data, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
