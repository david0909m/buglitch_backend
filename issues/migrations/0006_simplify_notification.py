# Generated manually for MVP notification simplification.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issues', '0005_issue_archived_at_issue_is_archived_commentimage_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='recipient',
            new_name='user',
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='Notification', max_length=120),
        ),
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(
                choices=[
                    ('issue_assigned', 'Issue assigned'),
                    ('issue_status_changed', 'Issue status changed'),
                    ('issue_commented', 'Issue commented'),
                    ('workspace_joined', 'Workspace joined'),
                ],
                default='issue_commented',
                max_length=40,
            ),
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='issue',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='event_type',
        ),
    ]
