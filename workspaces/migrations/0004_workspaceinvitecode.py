# Generated manually for MVP workspace invite codes.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workspaces', '0003_workspaceinvitation'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkspaceInviteCode',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'role',
                    models.CharField(
                        choices=[
                            ('owner', 'Owner'),
                            ('manager', 'Manager'),
                            ('developer', 'Developer'),
                            ('qa', 'QA'),
                        ],
                        default='developer',
                        max_length=20,
                    ),
                ),
                (
                    'code',
                    models.CharField(
                        editable=False,
                        max_length=20,
                        unique=True,
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(default=True),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='workspace_invite_codes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'workspace',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='invite_codes',
                        to='workspaces.workspace',
                    ),
                ),
            ],
        ),
    ]
