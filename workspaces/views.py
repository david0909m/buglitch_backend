from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Workspace, WorkspaceMembership
from .models import WorkspaceInviteCode
from .serializers import (
    WorkspaceSerializer,
    AddMemberSerializer,
    RemoveMemberSerializer,
    UpdateMemberRoleSerializer,
    WorkspaceMemberSerializer,
    CreateInviteCodeSerializer,
    WorkspaceInviteCodeSerializer,
    JoinWorkspaceSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from users.models import User

class WorkspaceViewSet(viewsets.ModelViewSet):

    serializer_class = WorkspaceSerializer

    permission_classes = [IsAuthenticated]

    manager_roles = ['owner', 'manager']

    def get_queryset(self):

        return Workspace.objects.prefetch_related(
            'memberships'
        ).filter(
            memberships__user=self.request.user
        ).distinct()

    def perform_create(self, serializer):

        workspace = serializer.save(
            created_by=self.request.user
        )

        WorkspaceMembership.objects.create(
            user=self.request.user,
            workspace=workspace,
            role='owner'
        )

    def get_user_membership(self, workspace, user):

        return WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=user
        ).first()

    def require_workspace_manager(self, workspace, user):

        membership = self.get_user_membership(workspace, user)

        if not membership or membership.role not in self.manager_roles:
            raise PermissionDenied(
                'Only workspace owners or managers can perform this action.'
            )

        return membership

    def require_workspace_owner(self, workspace, user):

        membership = self.get_user_membership(workspace, user)

        if not membership or membership.role != 'owner':
            raise PermissionDenied(
                'Only workspace owners can perform this action.'
            )

        return membership

    def require_owner_for_owner_role_changes(self, workspace, request_user, target_role, next_role=None):

        requester_membership = self.get_user_membership(workspace, request_user)
        touches_owner_role = target_role == 'owner' or next_role == 'owner'

        if touches_owner_role and (
            not requester_membership or requester_membership.role != 'owner'
        ):
            raise PermissionDenied(
                'Only workspace owners can manage owner roles.'
            )

    def ensure_workspace_keeps_owner(self, membership, next_role=None):

        if membership.role != 'owner':
            return

        if next_role == 'owner':
            return

        owner_count = WorkspaceMembership.objects.filter(
            workspace=membership.workspace,
            role='owner'
        ).count()

        if owner_count <= 1:
            raise PermissionDenied(
                'The workspace must keep at least one owner.'
            )

    def perform_update(self, serializer):

        self.require_workspace_manager(
            serializer.instance,
            self.request.user
        )

        serializer.save()

    def perform_destroy(self, instance):

        self.require_workspace_owner(
            instance,
            self.request.user
        )

        instance.delete()
    
    @action(detail=True, methods=['post'])

    def add_member(self, request, pk=None):
        
        workspace = self.get_object()

        self.require_workspace_manager(workspace, request.user)

        serializer = AddMemberSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data['role']

        self.require_owner_for_owner_role_changes(
            workspace,
            request.user,
            role
        )

        user = User.objects.get(id=user_id)

        membership, created = WorkspaceMembership.objects.get_or_create(
            user=user,
            workspace=workspace,
            defaults={'role': role}
        )

        if not created:
            self.require_owner_for_owner_role_changes(
                workspace,
                request.user,
                membership.role,
                role
            )
            self.ensure_workspace_keeps_owner(membership, role)
            membership.role = role
            membership.save()

        return Response({
            'detail': f'{user.username} has been added to the workspace with the role of {role}.'
        })

    @action(detail=True, methods=['post'])

    def update_member_role(self, request, pk=None):

        workspace = self.get_object()

        self.require_workspace_manager(workspace, request.user)

        serializer = UpdateMemberRoleSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data['role']

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace,
            user_id=user_id
        ).first()

        if not membership:
            raise PermissionDenied(
                'This user is not a member of this workspace.'
            )

        self.require_owner_for_owner_role_changes(
            workspace,
            request.user,
            membership.role,
            role
        )

        self.ensure_workspace_keeps_owner(membership, role)

        membership.role = role
        membership.save()

        return Response({
            'detail': f'{membership.user.username} role has been updated to {role}.'
        })

    @action(detail=True, methods=['post'])

    def remove_member(self, request, pk=None):

        workspace = self.get_object()

        self.require_workspace_manager(workspace, request.user)

        serializer = RemoveMemberSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace,
            user_id=serializer.validated_data['user_id']
        ).first()

        if not membership:
            raise PermissionDenied(
                'This user is not a member of this workspace.'
            )

        self.require_owner_for_owner_role_changes(
            workspace,
            request.user,
            membership.role
        )

        self.ensure_workspace_keeps_owner(membership)

        username = membership.user.username

        from issues.models import Issue

        Issue.objects.filter(
            project__workspace=workspace,
            assignee=membership.user
        ).update(assignee=None)

        membership.delete()

        return Response({
            'detail': f'{username} has been removed from the workspace.'
        })
    
    @action(detail=True, methods=['get'])

    def members(self, request, pk=None):
        
        workspace = self.get_object()

        if not WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=request.user
        ).exists():
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        memberships = WorkspaceMembership.objects.select_related(
            'user'
        ).filter(workspace=workspace)

        serializer = WorkspaceMemberSerializer(memberships, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])

    def my_role(self, request, pk=None):

        workspace = self.get_object()

        membership = self.get_user_membership(workspace, request.user)

        if not membership:
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        return Response({
            'workspace': workspace.id,
            'user': request.user.id,
            'role': membership.role,
            'can_manage_workspace': membership.role in self.manager_roles,
            'can_manage_owner_roles': membership.role == 'owner',
            'can_create_projects': membership.role in self.manager_roles,
        })

    @action(detail=True, methods=['post'], url_path='invite-code')

    def invite_code(self, request, pk=None):

        workspace = self.get_object()

        self.require_workspace_manager(workspace, request.user)

        serializer = CreateInviteCodeSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get('role', 'developer')

        self.require_owner_for_owner_role_changes(
            workspace,
            request.user,
            role
        )

        invite_code = WorkspaceInviteCode.objects.create(
            workspace=workspace,
            created_by=request.user,
            role=role
        )

        return Response(
            WorkspaceInviteCodeSerializer(invite_code).data,
            status=201
        )

    @action(detail=True, methods=['get'], url_path='invite-codes')

    def invite_codes(self, request, pk=None):

        workspace = self.get_object()

        self.require_workspace_manager(workspace, request.user)

        invite_codes = WorkspaceInviteCode.objects.filter(
            workspace=workspace,
            is_active=True
        ).order_by('-created_at')

        page = self.paginate_queryset(invite_codes)

        if page is not None:
            serializer = WorkspaceInviteCodeSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = WorkspaceInviteCodeSerializer(invite_codes, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])

    def join(self, request):

        serializer = JoinWorkspaceSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        invite_code = WorkspaceInviteCode.objects.select_related(
            'workspace'
        ).filter(
            code=serializer.validated_data['code'],
            is_active=True
        ).first()

        if not invite_code:
            raise PermissionDenied(
                'Invite code is invalid or inactive.'
            )

        membership, created = WorkspaceMembership.objects.update_or_create(
            workspace=invite_code.workspace,
            user=request.user,
            defaults={'role': invite_code.role}
        )

        from issues.models import Notification

        if created:
            Notification.objects.create(
                user=request.user,
                title='Workspace joined',
                message=f'You joined {invite_code.workspace.name} as {invite_code.role}.',
                type='workspace_joined'
            )

        return Response({
            'detail': 'Workspace joined.',
            'workspace': invite_code.workspace.id,
            'workspace_name': invite_code.workspace.name,
            'role': membership.role,
        })
