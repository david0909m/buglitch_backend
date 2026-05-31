from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import (
    Issue,
    Comment,
    IssueImage,
    CommentImage,
    Notification
)
from .serializers import (
    IssueSerializer,
    IssueStatusSerializer,
    IssueAssigneeSerializer,
    CommentSerializer,
    NotificationSerializer
)

from workspaces.models import WorkspaceMembership
from users.models import User


class IssueViewSet(viewsets.ModelViewSet):

    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    manager_roles = ['owner', 'manager']

    def get_queryset(self):

        queryset = Issue.objects.select_related(
            'project',
            'project__workspace',
            'reporter',
            'assignee'
        ).prefetch_related(
            'images'
        ).filter(
            project__workspace__memberships__user=self.request.user
        ).distinct()

        include_archived = (
            self.request.query_params.get('include_archived') == 'true' or
            self.action == 'restore'
        )

        if not include_archived:
            queryset = queryset.filter(
                is_archived=False,
                project__is_archived=False
            )

        project_id = self.request.query_params.get('project')
        status_param = self.request.query_params.get('status')
        assignee_id = self.request.query_params.get('assignee')
        priority = self.request.query_params.get('priority')
        search = self.request.query_params.get('search', '').strip()

        if project_id:

            if not project_id.isdigit():
                raise ValidationError({
                    'project': 'Project must be a valid ID.'
                })

            queryset = queryset.filter(project_id=project_id)

        if status_param:

            allowed_statuses = [
                status_value for status_value, status_label in Issue.STATUS_CHOICES
            ]

            if status_param not in allowed_statuses:
                raise ValidationError({
                    'status': 'Status must be one of: todo, progress, done.'
                })

            queryset = queryset.filter(status=status_param)

        if assignee_id:

            if not assignee_id.isdigit():
                raise ValidationError({
                    'assignee': 'Assignee must be a valid user ID.'
                })

            queryset = queryset.filter(assignee_id=assignee_id)

        if priority:

            allowed_priorities = [
                priority_value for priority_value, priority_label in Issue.PRIORITY_CHOICES
            ]

            if priority not in allowed_priorities:
                raise ValidationError({
                    'priority': 'Priority must be one of: low, medium, high.'
                })

            queryset = queryset.filter(priority=priority)

        if search:

            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def create_notification(self, user, actor, title, message, notification_type):

        if user and user != actor:
            Notification.objects.create(
                user=user,
                title=title,
                message=message,
                type=notification_type
            )

    def notify_issue_comment(self, issue, comment):

        recipients = {
            issue.reporter,
            issue.assignee,
        }

        for recipient in recipients:
            self.create_notification(
                user=recipient,
                actor=comment.author,
                title='New comment',
                notification_type='issue_commented',
                message=f'{comment.author.username} commented on {issue.title}.'
            )

    def get_workspace_membership(self, workspace):

        return WorkspaceMembership.objects.filter(
            workspace=workspace,
            user=self.request.user
        ).first()

    def require_workspace_member(self, workspace):

        membership = self.get_workspace_membership(workspace)

        if not membership:
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        return membership

    def require_issue_manager(self, issue):

        membership = self.require_workspace_member(issue.project.workspace)

        if membership.role not in self.manager_roles:
            raise PermissionDenied(
                'Only workspace owners or managers can modify issues.'
            )

        return membership

    def require_issue_status_permission(self, issue):

        membership = self.require_workspace_member(issue.project.workspace)

        if membership.role in self.manager_roles:
            return membership

        is_assigned_developer = (
            membership.role == 'developer' and
            issue.assignee_id == self.request.user.id
        )

        if is_assigned_developer:
            return membership

        raise PermissionDenied(
            'Only owners, managers, or the assigned developer can update issue status.'
        )

    def perform_create(self, serializer):

        project = serializer.validated_data['project']

        self.require_workspace_member(project.workspace)

        issue = serializer.save(
            reporter=self.request.user
        )

        for image in self.request.FILES.getlist('images'):
            IssueImage.objects.create(
                issue=issue,
                image=image,
                uploaded_by=self.request.user
            )

    def perform_update(self, serializer):

        issue = serializer.instance
        project = serializer.validated_data.get('project', issue.project)

        self.require_issue_manager(issue)

        if project != issue.project:
            membership = self.require_workspace_member(project.workspace)

            if membership.role not in self.manager_roles:
                raise PermissionDenied(
                    'Only workspace owners or managers can move issues between projects.'
                )

        serializer.save()

    def perform_destroy(self, instance):

        self.require_issue_manager(instance)

        instance.archive()

    @action(detail=True, methods=['post', 'patch'])
    def update_status(self, request, pk=None):

        issue = self.get_object()

        self.require_issue_status_permission(issue)

        serializer = IssueStatusSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        issue.status = serializer.validated_data['status']
        issue.save(update_fields=['status', 'updated_at'])

        self.create_notification(
            user=issue.reporter,
            actor=request.user,
            title='Issue status changed',
            notification_type='issue_status_changed',
            message=f'{request.user.username} moved {issue.title} to {issue.status}.'
        )

        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['post', 'patch'])
    def assign(self, request, pk=None):

        issue = self.get_object()

        self.require_issue_manager(issue)

        serializer = IssueAssigneeSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        assignee_id = serializer.validated_data.get('assignee')

        if assignee_id is None:
            issue.assignee = None
        else:
            assignee = User.objects.filter(id=assignee_id).first()

            if not assignee:
                raise ValidationError({
                    'assignee': 'User with this ID does not exist.'
                })

            membership_exists = WorkspaceMembership.objects.filter(
                workspace=issue.project.workspace,
                user=assignee
            ).exists()

            if not membership_exists:
                raise ValidationError({
                    'assignee': 'User is not a member of this workspace.'
                })

            issue.assignee = assignee

        issue.save(update_fields=['assignee', 'updated_at'])

        self.create_notification(
            user=issue.assignee,
            actor=request.user,
            title='Issue assigned',
            notification_type='issue_assigned',
            message=f'{request.user.username} assigned {issue.title} to you.'
        )

        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['post', 'patch'])
    def archive(self, request, pk=None):

        issue = self.get_object()

        self.require_issue_manager(issue)

        issue.archive()

        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['post', 'patch'])
    def restore(self, request, pk=None):

        issue = self.get_object()

        self.require_issue_manager(issue)

        if issue.project.is_archived:
            raise ValidationError({
                'project': 'Cannot restore an issue inside an archived project.'
            })

        issue.restore()

        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):

        issue = self.get_object()

        self.require_workspace_member(issue.project.workspace)

        images = request.FILES.getlist('images')

        if not images:
            raise ValidationError({
                'images': 'Upload at least one image.'
            })

        for image in images:
            IssueImage.objects.create(
                issue=issue,
                image=image,
                uploaded_by=request.user
            )

        return Response(self.get_serializer(issue).data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):

        issue = self.get_object()

        membership_exists = WorkspaceMembership.objects.filter(
            workspace=issue.project.workspace,
            user=request.user
        ).exists()

        if not membership_exists:
            raise PermissionDenied(
                'You are not a member of this workspace.'
            )

        if request.method == 'GET':

            comments = Comment.objects.select_related(
                'author'
            ).prefetch_related(
                'images'
            ).filter(
                issue=issue
            ).order_by('created_at')

            page = self.paginate_queryset(comments)

            if page is not None:
                serializer = CommentSerializer(
                    page,
                    many=True,
                    context={'request': request}
                )

                return self.get_paginated_response(serializer.data)

            serializer = CommentSerializer(
                comments,
                many=True,
                context={'request': request}
            )

            return Response(serializer.data)

        serializer = CommentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            issue=issue,
            author=request.user
        )

        for image in request.FILES.getlist('images'):
            CommentImage.objects.create(
                comment=comment,
                image=image,
                uploaded_by=request.user
            )

        self.notify_issue_comment(issue, comment)

        response_serializer = CommentSerializer(
            comment,
            context={'request': request}
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Notification.objects.filter(
            user=self.request.user
        )

        is_read = self.request.query_params.get('is_read')

        if is_read == 'true':
            queryset = queryset.filter(is_read=True)
        elif is_read == 'false':
            queryset = queryset.filter(is_read=False)

        return queryset

    @action(detail=True, methods=['post', 'patch'])
    def mark_read(self, request, pk=None):

        notification = self.get_object()

        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post', 'patch'])
    def mark_all_read(self, request):

        updated = self.get_queryset().filter(
            is_read=False
        ).update(is_read=True)

        return Response({
            'updated': updated
        })
