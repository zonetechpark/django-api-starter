from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

PASSWORD = 'pAssw0rd!'


class AuthenticationTest(APITestCase):

    def test_user_can_sign_up(self):
        """User can sign up"""
        response = self.client.post(reverse('user:signup'), data={
            'email': 'user@example.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password': PASSWORD,
        })
        user = get_user_model().objects.last()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['id'], str(user.id))
        self.assertEqual(response.data['lastname'], user.lastname)
        self.assertEqual(response.data['firstname'], user.firstname)