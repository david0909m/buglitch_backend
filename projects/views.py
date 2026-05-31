from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project
from .serializers import ProjectSerializer

from workspaces.models import WorkspaceMembership


class ProjectViewSet(viewsets.ModelViewSet):

    serializer_class = ProjectSerializer

    permission_classes = [IsAuthenticated]

    manager_roles = ['owner', 'manager']

    def get_queryset(self):

        queryset = Project.objects.select_related(
            'workspace',
            'created_by'
        ).filter(
            workspace__memberships__user=self.request.user
        ).distinct()

        include_archived = (
            self.request.query_params.get('include_archived') == 'true' or
            self.action == 'restore'
        )

        if not include_archived:
            queryset = queryset.filter(is_archived=False)

        workspace_id = self.request.query_params.get('workspace')

        if workspace_id:

            if not workspace_id.isdigit():
                raise ValidationError({
                    'workspace': 'Workspace must be a valid ID.'
                })

            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset

    def perform_create(self, serializer):

        workspace = serializer.validated_data['workspace']

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

        if not membership:
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        if membership.role not in self.manager_roles:
            raise PermissionDenied(
                'Only workspace owners or managers can create projects.'
            )

        serializer.save(
            created_by=self.request.user
        )

    def require_workspace_manager(self, workspace):

        membership = WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

        if not membership:
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        if membership.role not in self.manager_roles:
            raise PermissionDenied(
                'Only workspace owners or managers can modify projects.'
            )

        return membership

    def perform_update(self, serializer):

        workspace = serializer.validated_data.get(
            'workspace',
            serializer.instance.workspace
        )

        self.require_workspace_manager(serializer.instance.workspace)
        self.require_workspace_manager(workspace)

        serializer.save()

    def perform_destroy(self, instance):

        self.require_workspace_manager(instance.workspace)

        instance.archive()

    @action(detail=True, methods=['post', 'patch'])
    def archive(self, request, pk=None):

        project = self.get_object()

        self.require_workspace_manager(project.workspace)

        project.archive()

        return Response(ProjectSerializer(project).data)

    @action(detail=True, methods=['post', 'patch'])
    def restore(self, request, pk=None):

        project = self.get_object()

        self.require_workspace_manager(project.workspace)

        project.restore()

        return Response(ProjectSerializer(project).data)
