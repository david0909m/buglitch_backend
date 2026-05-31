from django.db import models
from django.conf import settings
from django.utils import timezone

from workspaces.models import Workspace


class Project(models.Model):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )

    is_archived = models.BooleanField(default=False)

    archived_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=['is_archived', 'archived_at', 'updated_at'])

    def restore(self):
        self.is_archived = False
        self.archived_at = None
        self.save(update_fields=['is_archived', 'archived_at', 'updated_at'])

    def __str__(self):
        return self.name
