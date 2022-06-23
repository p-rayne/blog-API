from django.contrib.auth import get_user_model
from django.test import TestCase

from account.serializer import UserSerializer

UserModel = get_user_model()


class UserSerializerTestCase(TestCase):
    def setUp(self):
        email = 'john.doe@example.com'
        password = '123456super'
        self.user = UserModel.objects.create_user(email, password)

    def test_ok(self):
        data = UserSerializer(self.user).data
        expected_data = {
            'id': self.user.id,
            'email': 'john.doe@example.com',
        }
        self.assertEqual(expected_data, data)
