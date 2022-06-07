from django.contrib.auth import get_user_model
from django.test import TestCase

from account.serializer import UserSerializer

UserModel = get_user_model()


class UserSerializerTestCase(TestCase):
    def test_ok(self):
        email = 'john.doe@example.com'
        password = '123456super'
        user = UserModel.objects.create_user(email, password)

        email2 = 'jane.doe@example.com'
        password2 = '123456super'
        user2 = UserModel.objects.create_user(email2, password2)
        data = UserSerializer([user, user2], many=True).data
        expected_data = [
            {
                'id': user.id,
                'email': 'john.doe@example.com',
            },
            {'id': user2.id,
             'email': 'jane.doe@example.com',
             },
        ]
        self.assertEqual(expected_data, data)
