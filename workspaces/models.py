from django.db import models
from django.conf import settings
import uuid
import secrets
import string


class Workspace(models.Model):

    name = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True
    )

    def __str__(self):
        return self.name


class WorkspaceMembership(models.Model):

    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('qa', 'QA'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workspace')

    def __str__(self):

        return f'{self.user.username} - {self.workspace.name}'


class WorkspaceInvitation(models.Model):

    email = models.EmailField()

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='invitations'
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_invitations_sent'
    )

    role = models.CharField(
        max_length=20,
        choices=WorkspaceMembership.ROLE_CHOICES
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'workspace', 'accepted_at')

    def __str__(self):
        return f'{self.email} -> {self.workspace.name}'


class WorkspaceInviteCode(models.Model):

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='invite_codes'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspace_invite_codes'
    )

    role = models.CharField(
        max_length=20,
        choices=WorkspaceMembership.ROLE_CHOICES,
        default='developer'
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_code():

        alphabet = string.ascii_uppercase + string.digits

        while True:
            suffix = ''.join(secrets.choice(alphabet) for i in range(6))
            code = f'BUG-{suffix}'

            if not WorkspaceInviteCode.objects.filter(code=code).exists():
                return code

    def save(self, *args, **kwargs):

        if not self.code:
            self.code = self.generate_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} -> {self.workspace.name}'
