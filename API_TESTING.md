# API testing guide

Base URL:

```text
http://127.0.0.1:8000
```

Test users:

```text
qa_user / qa_12345
dev_user / dev_12345
pm_user / pm_12345
```

## Auth

Get JWT tokens:

```text
POST /api/token/
```

Body:

```json
{
  "username": "pm_user",
  "password": "pm_12345"
}
```

Use the access token in the next requests:

```text
Authorization: Bearer <access>
```

Register now also returns `access` and `refresh`:

```text
POST /api/users/register/
```

## Workspace roles

Check the current user's role in a workspace:

```text
GET /api/workspaces/1/my_role/
```

Expected use:

```text
owner, manager, developer, qa
```

List members:

```text
GET /api/workspaces/1/members/
```

Expected use:

```text
Any workspace member.
```

Add a member:

```text
POST /api/workspaces/1/add_member/
```

Body:

```json
{
  "user_id": 2,
  "role": "developer"
}
```

Expected use:

```text
owner or manager.
Only owner can add another owner.
```

Update member role:

```text
POST /api/workspaces/1/update_member_role/
```

Body:

```json
{
  "user_id": 2,
  "role": "qa"
}
```

Expected use:

```text
owner or manager.
Only owner can modify owner roles.
The last owner cannot be demoted.
```

Remove member:

```text
POST /api/workspaces/1/remove_member/
```

Body:

```json
{
  "user_id": 2
}
```

Expected use:

```text
owner or manager.
Only owner can remove another owner.
The last owner cannot be removed.
```

## Projects

Filter projects by workspace:

```text
GET /api/projects/?workspace=1
```

Expected use:

```text
Any workspace member can list visible projects.
```

Create project:

```text
POST /api/projects/
```

Body:

```json
{
  "workspace": 1,
  "name": "Mobile app",
  "description": "Flutter client"
}
```

Expected use:

```text
owner or manager.
```

Update or delete project:

```text
PATCH /api/projects/1/
DELETE /api/projects/1/
```

Expected use:

```text
owner or manager.
```

## Issues and Kanban

List issues for a project:

```text
GET /api/issues/?project=1
```

Filter by Kanban status:

```text
GET /api/issues/?project=1&status=todo
GET /api/issues/?project=1&status=progress
GET /api/issues/?project=1&status=done
```

Filter by assignee:

```text
GET /api/issues/?project=1&assignee=2
```

Expected use:

```text
Any workspace member.
```

Create issue:

```text
POST /api/issues/
```

Body:

```json
{
  "project": 1,
  "title": "Login button fails",
  "description": "Button does not submit credentials.",
  "priority": "high",
  "status": "todo",
  "assignee": 2
}
```

Expected use:

```text
Any workspace member, useful for qa_user.
Assignee must belong to the same workspace.
```

Assign issue:

```text
PATCH /api/issues/1/assign/
```

Body:

```json
{
  "assignee": 2
}
```

Unassign issue:

```text
PATCH /api/issues/1/assign/
```

Body:

```json
{
  "assignee": null
}
```

Expected use:

```text
owner or manager, useful for pm_user.
```

Move issue in Kanban:

```text
PATCH /api/issues/1/update_status/
```

Body:

```json
{
  "status": "progress"
}
```

Expected use:

```text
owner, manager, or assigned developer.
Useful for pm_user and for dev_user when the issue is assigned to dev_user.
```

Issue comments:

```text
GET /api/issues/1/comments/
POST /api/issues/1/comments/
```

Body:

```json
{
  "content": "I reproduced this on Android."
}
```

Expected use:

```text
Any workspace member.
```
