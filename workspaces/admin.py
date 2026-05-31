from django.contrib import admin
from .models import (
    Workspace,
    WorkspaceMembership,
    WorkspaceInvitation,
    WorkspaceInviteCode
)

admin.site.register(Workspace)
admin.site.register(WorkspaceMembership)
admin.site.register(WorkspaceInvitation)
admin.site.register(WorkspaceInviteCode)
