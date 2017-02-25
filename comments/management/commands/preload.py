from rest_framework.test import APIClient

from django.core.management import BaseCommand

from comments.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.create(username='User_One', password='passwd')
        User.objects.create(username='User_Two', password='passwd2')
        User.objects.create(username='User_Three', password='passwd3')

        client = APIClient()

        data = {'entity_id': 3, "entity_type": 3, "comment": "Comment level INIT", "user": 1}
        client.post('/create/', data, format="json")

        for i in range(1,15):
            data = {'entity_id': i, "entity_type": 1, "comment": "Comment level {0}".format(i), "user": 2}
            client.post('/create/', data, format="json")

        for i in range(1,10):
            for u in range(1,3):
                data = {'entity_id': 2, "entity_type": 3, "comment": "F comment#{} by user#{}".format(i, u), "user": u}
                client.post('/create/', data, format='json')
