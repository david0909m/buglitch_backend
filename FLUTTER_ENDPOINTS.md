# Flutter endpoints

Base URL local:

```text
http://127.0.0.1:8000
```

All private endpoints require:

```text
Authorization: Bearer <access_token>
```

Paginated list responses return:

```json
{
  "count": 30,
  "next": "http://127.0.0.1:8000/api/issues/?page=2",
  "previous": null,
  "results": []
}
```

## 1. Auth flow

### Login

```text
POST /api/token/
```

Use in Flutter:

```text
Login screen.
```

Body:

```json
{
  "username": "pm_user",
  "password": "pm_12345"
}
```

Response:

```json
{
  "refresh": "...",
  "access": "..."
}
```

Next step:

```text
Save tokens with flutter_secure_storage.
```

### Refresh access token

```text
POST /api/token/refresh/
```

Use in Flutter:

```text
HTTP interceptor when access token expires.
```

Body:

```json
{
  "refresh": "<refresh_token>"
}
```

### Register with automatic login

```text
POST /api/users/register/
```

Use in Flutter:

```text
Register screen.
```

Body:

```json
{
  "username": "new_user",
  "email": "new@example.com",
  "password": "new_12345"
}
```

Response includes:

```text
user, access, refresh
```

## 2. Current user

### Me

```text
GET /api/users/me/
```

Use in Flutter:

```text
Splash/Auth check, profile menu, app header.
```

Roles:

```text
Any logged-in user.
```

### Search users

```text
GET /api/users/search/?q=dev
```

Use in Flutter:

```text
Member management screen, issue assignee picker.
```

Roles:

```text
Any logged-in user can search users.
The action after search is still protected by workspace permissions.
```

Next adjustment:

```text
Later, limit search to users already related to the organization.
```

## 3. Workspaces

### List workspaces

```text
GET /api/workspaces/
```

Use in Flutter:

```text
Workspace selector.
```

Roles:

```text
Any logged-in user. Returns only workspaces where the user is a member.
```

### Create workspace

```text
POST /api/workspaces/
```

Use in Flutter:

```text
Empty state, create workspace screen.
```

Body:

```json
{
  "name": "Buglitch Team"
}
```

Roles:

```text
Any logged-in user. Creator becomes owner automatically.
```

### Current role in workspace

```text
GET /api/workspaces/1/my_role/
```

Use in Flutter:

```text
Dashboard, project list, member management, conditional buttons.
```

Roles:

```text
Any workspace member.
```

Response includes:

```text
role, can_manage_workspace, can_manage_owner_roles, can_create_projects
```

### List workspace members

```text
GET /api/workspaces/1/members/
```

Use in Flutter:

```text
Members screen, assignee selector.
```

Roles:

```text
Any workspace member.
```

### Add member

```text
POST /api/workspaces/1/add_member/
```

Use in Flutter:

```text
Members screen.
```

Body:

```json
{
  "user_id": 2,
  "role": "developer"
}
```

Roles:

```text
owner or manager.
Only owner can add another owner.
```

### Update member role

```text
POST /api/workspaces/1/update_member_role/
```

Use in Flutter:

```text
Members screen, role dropdown.
```

Body:

```json
{
  "user_id": 2,
  "role": "qa"
}
```

Roles:

```text
owner or manager.
Only owner can manage owner roles.
Last owner cannot be demoted.
```

### Remove member

```text
POST /api/workspaces/1/remove_member/
```

Use in Flutter:

```text
Members screen.
```

Body:

```json
{
  "user_id": 2
}
```

Roles:

```text
owner or manager.
Only owner can remove another owner.
Last owner cannot be removed.
```

Next adjustment:

```text
When removing a member, add automatic unassign or require issue reassignment.
```

Current behavior:

```text
Assigned issues are automatically unassigned when a member is removed.
```

### Create invite code

```text
POST /api/workspaces/1/invite-code/
```

Use in Flutter:

```text
Members screen, generate workspace join code.
```

Body:

```json
{
  "role": "developer"
}
```

Roles:

```text
owner or manager.
Only owner can create an owner invite code.
```

Response includes:

```text
code, for example BUG-8F3K2A
```

Next adjustment:

```text
Add expiration or max uses when the MVP needs stricter control.
```

### List active invite codes

```text
GET /api/workspaces/1/invite-codes/
```

Roles:

```text
owner or manager.
```

### Join workspace by code

```text
POST /api/workspaces/join/
```

Use in Flutter:

```text
Join workspace screen.
```

Body:

```json
{
  "code": "BUG-8F3K2A"
}
```

Roles:

```text
Any logged-in user with a valid active code.
```

## 4. Projects

### List projects by workspace

```text
GET /api/projects/?workspace=1
```

Use in Flutter:

```text
Workspace dashboard, project list.
```

Roles:

```text
Any workspace member.
```

### Create project

```text
POST /api/projects/
```

Use in Flutter:

```text
Create project screen or dialog.
```

Body:

```json
{
  "workspace": 1,
  "name": "Flutter App",
  "description": "Mobile client"
}
```

Roles:

```text
owner or manager.
Use this with pm_user when pm_user has manager role.
```

### Update project

```text
PATCH /api/projects/1/
```

Roles:

```text
owner or manager.
```

### Delete project

```text
DELETE /api/projects/1/
```

Roles:

```text
owner or manager.
```

Current behavior:

```text
DELETE archives the project instead of permanently deleting it.
```

### Archive project

```text
PATCH /api/projects/1/archive/
```

Roles:

```text
owner or manager.
```

### Restore project

```text
PATCH /api/projects/1/restore/
```

Roles:

```text
owner or manager.
```

### Include archived projects

```text
GET /api/projects/?workspace=1&include_archived=true
```

Use in Flutter:

```text
Archived projects screen.
```

Next adjustment:

```text
Add a separate permanent-delete endpoint only for admin/superuser if ever needed.
```

## 5. Issues and Kanban

### List issues by project

```text
GET /api/issues/?project=1
```

Use in Flutter:

```text
Kanban board initial load.
```

Roles:

```text
Any workspace member.
```

### List issues by Kanban column

```text
GET /api/issues/?project=1&status=todo
GET /api/issues/?project=1&status=progress
GET /api/issues/?project=1&status=done
```

Use in Flutter:

```text
Kanban columns.
```

### Filter issues by assignee

```text
GET /api/issues/?project=1&assignee=2
```

Use in Flutter:

```text
My tasks, assignee filter.
```

### Filter issues by priority

```text
GET /api/issues/?project=1&priority=high
```

Use in Flutter:

```text
Priority filter chips.
```

### Search issues

```text
GET /api/issues/?project=1&search=login
```

Use in Flutter:

```text
Kanban search bar.
```

### Create issue

```text
POST /api/issues/
```

Use in Flutter:

```text
Create issue screen, useful for qa_user.
```

Body:

```json
{
  "project": 1,
  "title": "Login fails",
  "description": "The login button does not submit credentials.",
  "priority": "high",
  "status": "todo",
  "assignee": 2
}
```

Roles:

```text
Any workspace member.
Assignee must be a member of the same workspace.
```

To upload screenshots while creating an issue, send `multipart/form-data`:

```text
project=1
title=Login fails
description=The login button does not submit credentials.
priority=high
status=todo
assignee=2
images=<file1>
images=<file2>
```

In Flutter:

```text
Use MultipartRequest or Dio FormData with repeated images fields.
```

### Assign issue

```text
PATCH /api/issues/1/assign/
```

Use in Flutter:

```text
Issue detail, manager assignment action.
```

Body:

```json
{
  "assignee": 2
}
```

Unassign:

```json
{
  "assignee": null
}
```

Roles:

```text
owner or manager.
Use this with pm_user when pm_user has manager role.
```

### Move issue status

```text
PATCH /api/issues/1/update_status/
```

Use in Flutter:

```text
Kanban drag and drop.
```

Body:

```json
{
  "status": "progress"
}
```

Roles:

```text
owner, manager, or assigned developer.
Use with dev_user only when the issue is assigned to dev_user.
```

This creates a notification for the reporter when another user changes status.

### Update issue details

```text
PATCH /api/issues/1/
```

Use in Flutter:

```text
Issue detail edit form.
```

Roles:

```text
owner or manager.
```

### Archive issue

```text
PATCH /api/issues/1/archive/
```

Roles:

```text
owner or manager.
```

### Restore issue

```text
PATCH /api/issues/1/restore/
```

Roles:

```text
owner or manager.
Cannot restore issue if its project is archived.
```

### Include archived issues

```text
GET /api/issues/?project=1&include_archived=true
```

Use in Flutter:

```text
Archived issues screen.
```

### Upload image to existing issue

```text
POST /api/issues/1/upload_image/
```

Use in Flutter:

```text
Issue detail, add screenshot button.
```

Send as `multipart/form-data`:

```text
images=<file1>
images=<file2>
```

Roles:

```text
Any workspace member.
```

Next adjustment:

```text
Later, allow qa_user to edit only issues they reported if product rules require it.
```

## 6. Comments

### List comments

```text
GET /api/issues/1/comments/
```

Use in Flutter:

```text
Issue detail conversation.
```

Roles:

```text
Any workspace member.
```

### Add comment

```text
POST /api/issues/1/comments/
```

Body:

```json
{
  "content": "Reproduced on Android emulator."
}
```

To add screenshots in the same comment, send `multipart/form-data`:

```text
content=Reproduced on Android emulator.
images=<file1>
images=<file2>
```

Roles:

```text
Any workspace member.
```

This creates notifications for the reporter and assignee, except the user who wrote the comment.

## 7. Notifications

### List notifications

```text
GET /api/notifications/
GET /api/notifications/?is_read=false
```

Use in Flutter:

```text
Notification center, dashboard badge.
```

Roles:

```text
Any logged-in user. Returns only the current user's notifications.
```

Response item:

```json
{
  "id": 1,
  "user": 2,
  "title": "Issue assigned",
  "message": "pm_user assigned Login fails to you.",
  "type": "issue_assigned",
  "is_read": false,
  "created_at": "2026-05-30T20:00:58Z"
}
```

### Mark notification as read

```text
PATCH /api/notifications/1/mark_read/
```

### Mark all notifications as read

```text
PATCH /api/notifications/mark_all_read/
```

Next adjustment:

```text
Later, add notification counts by workspace or issue if the UI needs badges per section.
```

Next adjustment:

```text
Add edit/delete comment rules later: author can edit own comment, owner/manager can moderate.
```

## Suggested Flutter order

1. Build auth service: login, register, refresh, logout.
2. Build token interceptor with automatic refresh.
3. Build workspace selector and `my_role` role cache.
4. Build project list filtered by workspace.
5. Build Kanban using `/api/issues/?project=<id>`.
6. Build issue detail with comments.
7. Build screenshots upload for issues and comments.
8. Build notifications badge/list.
9. Build member management and invite-code join flow for owner/manager.
10. Add user search for member and assignee pickers.

## Backend adjustments for later

1. Add expiration/max uses to invite codes.
2. Add audit log for role changes and status movements.
3. Add image compression/thumbnail generation.
4. Add file attachments beyond images, such as logs or PDFs.
5. Add object storage later, for example S3 or Cloudinary.
