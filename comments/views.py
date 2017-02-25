from rest_framework.views import APIView
from rest_framework import  viewsets, status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from django.http import Http404

from comments.models import CommentTree, User
from comments.utils import (
    MaterializedPathConvert,
    CommentsSerializer,
    CommentsPagination,
    CommentsSerializerUpdate
)


class CommentDetail(APIView):

    def get_object(self, pk):
        try:
            return CommentTree.objects.published().get(pk=pk)
        except CommentTree.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        comment = self.get_object(pk)
        serializer = CommentsSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        comment = self.get_object(pk)
        serializer = CommentsSerializerUpdate(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        comment = self.get_object(pk)
        if not CommentTree.objects.childs_exist(pk):
            comment.deleted = True
            comment.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Remove childs"}, status=status.HTTP_400_BAD_REQUEST)


class CommentChildView(APIView):
    """
    Get comment by ID with childs and convert to hierarchy dict
    """
    def get(self, request, pk, format=None):
        data = CommentTree.objects.childs(pk)
        result = list(map(lambda x: CommentsSerializer(x).data, data))
        result = MaterializedPathConvert(result).process()
        return Response(result)


class CommentLevelView(ListAPIView):
    """
    Get comment by Entity-Type / Entity-ID with pagination
    """
    serializer_class = CommentsSerializer
    pagination_class = CommentsPagination

    def get_queryset(self):
        entity_id = self.kwargs.get("entity_id")
        entity_type = self.kwargs.get("entity_type")
        return CommentTree.objects.by_level_with_entity_pair(int(entity_type), int(entity_id))


class CommentCreateBase:
    ENTITY = {v: k for k, v in dict(CommentTree.ENTITY).items()}


class CommentByPKCreateView(APIView, CommentCreateBase):
    """
    OPTIONAL class for quick add comments
    Create comment by pk
    """
    def post(self, request, format=None):
        comment_id = request.data.get("comment_id")

        try:
            comment_id = int(comment_id)
        except (ValueError, TypeError):
            return Response({"message": "PK must be integer"})

        response = self.create_comment(comment_id, request.data)
        return Response(response)

    def create_comment(self, parent_pk, data):
        entity_type = self.ENTITY["Comment"]

        try:
            parent = CommentTree.objects.get(pk=parent_pk)
        except CommentTree.DoesNotExist:
            return {"message": "Parent not found"}

        node = CommentTree.objects.create(
            entity_type=entity_type,
            entity_id=parent_pk,
            comment=data.get("comment"),
            path=parent.path
        )
        node.save()
        node.path.append(node.pk)
        node.save()
        return {"message": "Success"}


class CommentByEntityCreateView(APIView, CommentCreateBase):
    """
    Create comment by ENTITY
    """
    def post(self, request, format=None):
        entity_pk = request.data.get("entity_id")
        entity_type = request.data.get("entity_type")
        user_id = request.data.get("user")

        try:
            entity_pk = int(entity_pk)
            entity_type = int(entity_type)
            user_id = int(user_id)
        except (ValueError, TypeError):
            return Response({"message": "PK must be integer"}, status=status.HTTP_400_BAD_REQUEST)

        response, status = self.create_comment(entity_pk, entity_type, user_id, request.data)
        return Response(response, status=status)

    def create_comment(self, entity_id, entity_type, user_id, data):

        if self.ENTITY["Comment"] == entity_type:
            try:
                parent = CommentTree.objects.get(pk=entity_id)
                entity_id = parent.pk
            except (CommentTree.DoesNotExist, AttributeError):
                    return {"message": "Entity type is comment, but parent not found"}, status.HTTP_400_BAD_REQUEST

        node = CommentTree.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            comment=data.get("comment"),
            author=User.objects.get(pk=user_id), #check user exists
            path=parent.path if self.ENTITY["Comment"] == entity_type else []
        )
        node.save()
        node.path.append(node.pk)
        node.save()
        return {"message": "Success"}, status.HTTP_201_CREATED


class CommentsViewSet(viewsets.mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Optional view for views all comments
    """
    queryset = CommentTree.objects.published().all()
    serializer_class = CommentsSerializer
    pagination_class = CommentsPagination


class CommentsUserListView(ListAPIView):

    serializer_class = CommentsSerializer
    pagination_class = CommentsPagination

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return CommentTree.objects.published().filter(author__pk=pk)
