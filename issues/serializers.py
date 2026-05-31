from rest_framework import serializers

from .models import (
    Issue,
    Comment,
    IssueImage,
    CommentImage,
    Notification
)
from workspaces.models import WorkspaceMembership


class IssueImageSerializer(serializers.ModelSerializer):

    image_url = serializers.ImageField(
        source='image',
        read_only=True
    )

    uploaded_by = serializers.CharField(
        source='uploaded_by.username',
        read_only=True
    )

    class Meta:
        model = IssueImage
        fields = [
            'id',
            'image',
            'image_url',
            'uploaded_by',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'image',
            'image_url',
            'uploaded_by',
            'created_at',
        ]


class CommentImageSerializer(serializers.ModelSerializer):

    image_url = serializers.ImageField(
        source='image',
        read_only=True
    )

    uploaded_by = serializers.CharField(
        source='uploaded_by.username',
        read_only=True
    )

    class Meta:
        model = CommentImage
        fields = [
            'id',
            'image',
            'image_url',
            'uploaded_by',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'image',
            'image_url',
            'uploaded_by',
            'created_at',
        ]


class IssueSerializer(serializers.ModelSerializer):

    reporter = serializers.CharField(
        source='reporter.username',
        read_only=True
    )

    project_name = serializers.CharField(
        source='project.name',
        read_only=True
    )

    workspace = serializers.IntegerField(
        source='project.workspace_id',
        read_only=True
    )

    workspace_name = serializers.CharField(
        source='project.workspace.name',
        read_only=True
    )

    assignee_username = serializers.CharField(
        source='assignee.username',
        read_only=True
    )

    images = IssueImageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = [
            'reporter',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):

        project = attrs.get('project')
        assignee = attrs.get('assignee')

        if not project and self.instance:
            project = self.instance.project

        if assignee and project:

            membership_exists = WorkspaceMembership.objects.filter(
                workspace=project.workspace,
                user=assignee
            ).exists()

            if not membership_exists:
                raise serializers.ValidationError({
                    'assignee': 'User is not a member of this workspace.'
                })

        return attrs


class IssueStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        choices=Issue.STATUS_CHOICES
    )


class IssueAssigneeSerializer(serializers.Serializer):

    assignee = serializers.IntegerField(
        allow_null=True,
        required=True
    )


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.CharField(
        source='author.username',
        read_only=True
    )

    images = CommentImageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = [
            'author',
            'issue',
            'created_at',
            'updated_at',
        ]


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'title',
            'message',
            'type',
            'is_read',
            'created_at',
        ]
        read_only_fields = fields
