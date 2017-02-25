from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from comments.models import User


class CreateTestCase(APITestCase):
    def setUp(self):
        User.objects.create(username='User_One', password='passwd')
        User.objects.create(username='User_Two', password='passwd2')
        User.objects.create(username='User_Three', password='passwd3')

    def test_create_comment(self):
        url = reverse('create')
        data = {'entity_id': 3, "entity_type": "2", "comment": "First level comment", "user":1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'entity_id': 1, "entity_type": 1, "comment": "Second level comment", "user": 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message":"Success"})

        data = {'entity_id': 2, "entity_type": 1, "comment": "Third level comment", "user": 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "Success"})

        data = {'entity_id': 3, "entity_type": "2", "comment": "First level comment#2", "user":1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('child', kwargs={"pk": 1})
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["childs"][0]["childs"][0]["comment"], "Third level comment")

        url = reverse('comment-item', kwargs={"pk": 1})
        response = self.client.put(url, {"comment":"Changed comment"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"comment": "Changed comment"})

        url = reverse('comment-item', kwargs={"pk": 1})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "Remove childs"})

        url = reverse('comment-item', kwargs={"pk": 3})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('comment-item', kwargs={"pk": 2})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse('first-level', kwargs={"entity_type": 2, "entity_id": 3})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
