import os
import time
import uuid
import mimetypes
from datetime import datetime

from wsgiref.util import FileWrapper

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import StreamingHttpResponse

from comments.utils import RedisStore
from comments.models import CommentTree
from comments.utils import CommentsSerializer


class StreamWrapper:

    def wrapfile(self, filename):
        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(filename, 'rb'), chunk_size),
                                         content_type=mimetypes.guess_type(filename)[0])

        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = "attachment; filename={0}".format(filename)
        return response


class CommentsUserXML(APIView, StreamWrapper):
    parser_classes = (XMLParser,)
    renderer_classes = (XMLRenderer,)

    def __init__(self, *args, **kwargs):
        super(CommentsUserXML,self).__init__(*args, **kwargs)
        self.cached_query = False

    @classmethod
    def convert(cls, date_string):
        try:
            return datetime.strptime(date_string, '%Y-%m-%d')
        except (TypeError, ValueError):
            return False

    def create_range_query(self, data):

        date_from = self.convert(data.GET.get("from"))
        date_to = self.convert(data.GET.get("to"))

        if not date_to and date_from:
            return {"create_date__gte": date_from}

        if date_from and date_to:
            return {"create_date__range": (date_from, date_to)}

    def create_selector(self, data):
        entity_id = data.GET.get("entity_id")
        entity_type = data.GET.get("entity_type")

        user_pk = data.GET.get("user")

        if entity_id and entity_type:
            return {
                "entity_id": entity_id,
                "entity_type": entity_type
            }

        if user_pk:
            self.cached_query = True
            return {
                "author__pk": user_pk
            }

    def get(self, request, format=None):

        selector = self.create_selector(request)
        if not selector:
            return Response({"message": "Please set User or Entity pair"})

        data = CommentTree.objects.published().filter(**selector)

        date_range = self.create_range_query(request)
        if type(date_range) is dict:
            data = data.filter(**date_range)

        result = list(map(lambda x: CommentsSerializer(x).data, data))
        if not result:
            return Response({"message": "QuerySet empty"})

        result = XMLRenderer().render(result)

        # TO DO: Move to celery task
        filename = settings.PATH_TO_XML+"{0}.xml".format(uuid.uuid4())
        with open(filename, "w") as xml_file:
            xml_file = File(xml_file)
            xml_file.write(result)

        # If use USER in grequest.GET - cache this response
        if result: #and self.cached_query:
            RedisStore().add(filename)

        return self.wrapfile(filename)


class History(APIView, StreamWrapper):

    def get(self, request, pk=None, format=None):
        store = RedisStore()
        if not pk:
            keys = store.all()
            result = [map(lambda x: {time.ctime(int(x)): reverse("history-item", kwargs={'pk': int(x)})}, keys)]
            return Response(result)
        else:
            filename = store.get(pk)
            try:
                return self.wrapfile(str(filename))
            except (ValueError, TypeError, FileNotFoundError):
                return Response({"message": "Error while wrapping file"}, status=status.HTTP_404_NOT_FOUND)