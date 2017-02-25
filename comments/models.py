from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):

    full_name = models.CharField(
        max_length=255, null=True, blank=True)
    username = models.CharField(
        max_length=255, unique=True, null=True)

    USERNAME_FIELD = 'username'

    def __unicode__(self):
        return self.full_name or self.username or ''


class CommentTreeQueryManager(models.Manager):

    def published(self):
        return self.filter(deleted=False)

    def childs(self, parent):
        if parent:
            return self.published().filter(path__overlap=[parent]).extra(order_by={"path": "array_length(path, 1)"})

    def childs_exist(self, parent):
        if self.published().filter(path__overlap=[parent], path__len__gte=2).exclude(pk__in=[parent]).exists():
            return True

    def by_level(self, key, level=1):
        """
        Filter materialized tree by ID with level support
        """
        return self.filter(path__overlap=[key], path__len__lte=level).extra(order_by={"path": "array_length(path, 1)"})

    def by_level_with_entity_pair(self, entity_type, entity_id, level=1):
        """
        Filter materialized tree by ID or ENTITY ID with level support
        """
        if int(entity_type) == 1:
            parent = self.published().get(pk=int(entity_id))
            if parent.path:
                level = len(parent.path)+1

        return self.published().filter(path__len=level).filter(entity_id=entity_id, entity_type=entity_type).extra(
            order_by={"path": "array_length(path, 1)"})


class CommentTree(models.Model):

    objects = CommentTreeQueryManager()

    ENTITY = (
        (1, 'Comment'),
        (2, 'Profile'),
        (3, 'Post'),
    )

    path = ArrayField(models.IntegerField(), db_index=True)
    comment = models.CharField(max_length=500)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    author = models.ForeignKey(User, blank=False, null=False)

    # TO DO: through GENERIC relations
    entity_type = models.IntegerField(choices=ENTITY, default=1)
    entity_id = models.IntegerField(blank=False, null=False)

    def __unicode__(self):
        return self.comment

