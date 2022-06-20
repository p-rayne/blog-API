import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from post.models import UserFollowing

UserModel = get_user_model()


class BlogAPITestCase(APITestCase):
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

        for i in range(1, 4):
            self.user.posts.create(title=f'{self.user} title{i}', text=f'{self.user} Test text{i}')
        for i in range(1, 3):
            self.user2.posts.create(title=f'{self.user2} title{i}', text=f'{self.user2} Test text{i}')
        for i in range(1, 5):
            self.user3.posts.create(title=f'{self.user3} title{i}', text=f'{self.user3} Test text{i}')

    def test_blogAPI(self):
        email = 'user@example.com'
        # Create new user.
        url = reverse('users')
        data = {
            'email': email,
            'password': '123456super'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        # User authentication.
        url = reverse('knox_login')
        data = {
            'email': 'user@example.com',
            'password': '123456super'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        #  Creating a post.
        url = reverse('post_create')
        data = {
            'title': 'Test post title',
            'text': 'Test post text',
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        #  Getting a list of users.
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        #  Sorting the list of users by the number of posts in descending order.
        response = self.client.get(url, {'ordering': '-posts_count'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        #  Sorting the list of users by the number of posts in ascending order.
        response = self.client.get(url, {'ordering': 'posts_count'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        #  Get list of user's posts.
        url = reverse('user_posts', args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.user.posts.count(), len(response.data))
        url = reverse('user_posts', args=(self.user2.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.user2.posts.count(), len(response.data))

        #  Subscribe to user posts.
        url = reverse('follow')
        users = ('', self.user, self.user2, self.user3)
        for i in range(1, 4):
            data = {
                'following_user': users[i].pk
            }
            json_data = json.dumps(data)
            response = self.client.post(url, data=json_data,
                                        content_type='application/json')
            self.assertEqual(status.HTTP_201_CREATED, response.status_code)
            self.assertEqual(i, UserFollowing.objects.filter(user__email=email).count())

        #  Get list of subscriptions.
        url = reverse('follow')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.data))

        #  Unsubscribe from user posts.
        url = reverse('unfollow', args=(UserFollowing.objects.get(user__email=email, following_user=self.user2).pk,))
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, UserFollowing.objects.filter(user__email=email).count())

        for j in range(5, 12):
            self.user.posts.create(title=f'{self.user} title{j}', text=f'{self.user} Test text{j}')
        for i in range(6, 15):
            self.user3.posts.create(title=f'{self.user3} title{i}', text=f'{self.user3} Test text{i}')

        #  Get feed from user posts, on which have been subscribed.
        #  The list of posts is given in pages of 10 pieces.
        url = reverse('posts_feed')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dct = json.loads(response.content)
        total_posts = dct['count']
        posts_in_the_feed = [k['id'] for k in dct['results']]
        self.assertEqual(10, len(posts_in_the_feed))

        #  Mark posts as read.
        readed_posts = posts_in_the_feed[:5]
        for i in readed_posts:
            url = reverse('post_read', args=(i,))
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)

        #  Get only read posts.
        url = reverse('posts_feed')
        data = {
            'readed': 'true'
        }
        response = self.client.get(url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dct = json.loads(response.content)
        read_count = dct['count']
        self.assertEqual(read_count, len(readed_posts))
        posts_id_read = [k['id'] for k in dct['results']]
        self.assertEqual(posts_id_read, readed_posts)

        #  Get only unread messages.
        url = reverse('posts_feed')
        data = {
            'readed': 'false'
        }
        response = self.client.get(url, data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        dct = json.loads(response.content)
        self.assertEqual((total_posts - read_count), dct['count'])
        posts_id_unread = [k['id'] for k in dct['results']]
        self.assertNotIn(posts_id_read, posts_id_unread)
