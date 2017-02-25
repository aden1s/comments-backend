import time
import redis

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from comments.models import CommentTree


class RedisStore:

    KEY = "HISTORY"

    def __init__(self):
        self.connection = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

    def add(self, file_uuid):
        self.connection.hset(self.KEY, round(time.time()), str(file_uuid))

    def remove(self):
        pass

    def get(self, value):
        return self.connection.hget(self.KEY, str(value))

    def all(self):
        return self.connection.hkeys(self.KEY)


class CommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentTree
        fields = ('id', 'path', 'comment', "entity_type",
                  "entity_id", "create_date", "modified_date")


class CommentsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CommentsSerializerUpdate(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommentTree
        fields = ("comment",)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance


class MaterializedPathConvert:

    def __init__(self, materialized_dict):
        self.source = materialized_dict

    def process(self):
        root = []
        if not self.source or type(self.source) is not list:
            return []

        level = len(self.source[0]["path"])-1

        for item in self.source:
            self.insert(root, item, item["path"][level:-1])
        return root

    def insert(self, root, node, path):
        if not path:
            return root.append(node)

        for i in path:
            for item in root:
                if item["id"] == i:
                    if not item.get("childs"):
                        item["childs"] = []
                    self.insert(item["childs"], node, path[1:])

        return root