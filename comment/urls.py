from rest_framework import routers

from django.conf.urls import url, include

from comments.views import (
    CommentDetail,
    CommentsViewSet,
    CommentChildView,
    CommentLevelView,
    CommentsUserListView,
    CommentByEntityCreateView,
)
from comments.statviews import History, CommentsUserXML


router = routers.DefaultRouter()
router.register(r'comments', CommentsViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # Get information about comments
    url(r'^child/(?P<pk>[0-9]+)/$', CommentChildView.as_view(), name="child"),
    url(r'^first-level/(?P<entity_type>[0-9]+)/(?P<entity_id>[0-9]+)/$', CommentLevelView.as_view(), name="first-level"),
    url(r'^comment/(?P<pk>[0-9]+)/$', CommentDetail.as_view(), name="comment-item"),
    #Create post views
    url(r'^create/$', CommentByEntityCreateView.as_view(), name="create"),
    #History and XML-file format
    url(r'^history/(?P<pk>[0-9]+)/$', History.as_view(), name="history-item"),
    url(r'^history/$', History.as_view(), name="history"),
    url(r'^comments-user/(?P<pk>[0-9]+)/$', CommentsUserListView.as_view(), name="user-comments"),
    url(r'^comments-xml/$', CommentsUserXML.as_view(), name="comments-xml"),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
