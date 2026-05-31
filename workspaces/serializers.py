from rest_framework import serializers
from users.models import User
from .models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceInvitation,
    WorkspaceInviteCode
)


class WorkspaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workspace
        fields = '__all__'

        read_only_fields = [
            'created_by',
            'created_at',
        ]

class AddMemberSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=WorkspaceMembership.ROLE_CHOICES
    )

    def validate_user_id(self, value):

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'User with this ID does not exist.'
            )

        return value


class RemoveMemberSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()

    def validate_user_id(self, value):

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'User with this ID does not exist.'
            )

        return value


class UpdateMemberRoleSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=WorkspaceMembership.ROLE_CHOICES
    )

    def validate_user_id(self, value):

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'User with this ID does not exist.'
            )

        return value


class WorkspaceMemberSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.ChoiceField(choices=WorkspaceMembership.ROLE_CHOICES, read_only=True)
    class Meta:
        model = WorkspaceMembership
        fields = ['id', 'user_id', 'username', 'email', 'role'] 
        read_only_fields = ['id', 'user_id', 'username', 'email', 'role']


class WorkspaceInvitationSerializer(serializers.ModelSerializer):

    invited_by = serializers.CharField(
        source='invited_by.username',
        read_only=True
    )

    workspace_name = serializers.CharField(
        source='workspace.name',
        read_only=True
    )

    class Meta:
        model = WorkspaceInvitation
        fields = [
            'id',
            'email',
            'workspace',
            'workspace_name',
            'invited_by',
            'role',
            'token',
            'accepted_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'workspace',
            'workspace_name',
            'invited_by',
            'token',
            'accepted_at',
            'created_at',
        ]


class AcceptInvitationSerializer(serializers.Serializer):

    token = serializers.UUIDField()


class CreateInviteCodeSerializer(serializers.Serializer):

    role = serializers.ChoiceField(
        choices=WorkspaceMembership.ROLE_CHOICES,
        default='developer',
        required=False
    )


class WorkspaceInviteCodeSerializer(serializers.ModelSerializer):

    workspace_name = serializers.CharField(
        source='workspace.name',
        read_only=True
    )

    created_by = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    class Meta:
        model = WorkspaceInviteCode
        fields = [
            'id',
            'workspace',
            'workspace_name',
            'created_by',
            'role',
            'code',
            'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'workspace',
            'workspace_name',
            'created_by',
            'code',
            'created_at',
        ]


class JoinWorkspaceSerializer(serializers.Serializer):

    code = serializers.CharField(max_length=20)

    def validate_code(self, value):

        return value.strip().upper()
