from django.contrib.auth import get_user_model
from django.test import TestCase

from account.serializer import UserSerializer

UserModel = get_user_model()


class UserSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = UserModel.objects.create(email='test', password=12)
        user_2 = UserModel.objects.create(email='test@test.com', password='123456super')
        data = UserSerializer([user_1, user_2], many=True).data
        expected_data = [
            {
                'id': user_1.id,
                'email': 'test',
            },
            {'id': user_2.id,
             'email': 'test@test.com',
             },
        ]
        self.assertEqual(expected_data, data)
