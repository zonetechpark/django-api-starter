import json
import uuid
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from community.models import Puppy
from community.serializers import PuppySerializer

client = Client()


class GetAllPuppiesTest(TestCase):
    """Test modules to get all puppies API"""

    def setUp(self):
        Puppy.objects.create(name='Casper', age=4, breed='Bull Dog', color='Black')
        Puppy.objects.create(name='Muffin', age=3, breed='Gradane', color='Brown')
        Puppy.objects.create(name='Rambo', age=1, breed='Labrador', color='Black')
        Puppy.objects.create(name='Ricky', age=6, breed='Labrador', color='Brown')

    def test_get_all_puppies(self):
        response = client.get(reverse('puppy'))
        puppies = Puppy.objects.all()
        serializer = PuppySerializer(puppies, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSinglePuppyTest(TestCase):
    """Test module to GET single puppy API"""

    def setUp(self):
        self.casper = Puppy.objects.create(name='Casper', age=4, breed='Bull Dog', color='Black')
        self.muffin = Puppy.objects.create(name='Muffin', age=3, breed='Gradane', color='Brown')
        self.rambo = Puppy.objects.create(name='Rambo', age=1, breed='Labrador', color='Black')
        self.ricky = Puppy.objects.create(name='Ricky', age=6, breed='Labrador', color='Brown')

    def test_get_valid_single_puppy(self):
        response = client.get(reverse('puppy-detail', kwargs={'pk': self.rambo.pk}))
        puppy = Puppy.objects.get(pk=self.rambo.pk)
        serializer = PuppySerializer(puppy)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_single_invalid_puppy(self):
        response = client.get(reverse('puppy-detail', kwargs={'pk': uuid.uuid4()}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewPuppyTest(TestCase):
    """Test module for inserting new puppy"""

    def setUp(self):
        self.valid_payload = {
            "name": "Muffin",
            "age": 4,
            "breed": "Pamerion",
            "color": "White"
        }
        self.invalid_payload = {
            "name": "",
            "age": 4,
            "breed": "Pamerion",
            "color": "White"
        }

    def test_create_valid_puppy(self):
        response = client.post(reverse('puppy'), data=json.dumps(self.valid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_payload(self):
        response = client.post(reverse('puppy'), data=json.dumps(self.invalid_payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
