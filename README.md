# Buglitch Backend

Backend Django REST para **Buglitch**, una aplicacion tipo SaaS para bug tracking orientada a equipos de desarrollo o QA. El proyecto permite trabajar con workspaces, roles por equipo, proyectos, issues estilo Kanban, comentarios con imagenes, notificaciones internas y codigos de invitacion.

La intencion del proyecto es servir como base backend para una app Flutter donde un equipo pueda reportar, asignar, comentar y dar seguimiento a errores encontrados durante pruebas de software.

## Estado del Proyecto

Este backend ya cubre el flujo MVP necesario para comenzar el frontend Flutter:

- Registro y login con JWT.
- Usuarios globales.
- Workspaces multiusuario.
- Roles contextuales por workspace: `owner`, `manager`, `developer`, `qa`.
- Codigos de invitacion para unirse a workspaces.
- Proyectos asociados a workspaces.
- Issues asociados a proyectos.
- Filtros para Kanban por proyecto, status, prioridad, asignado y busqueda.
- Comentarios por issue.
- Imagenes en issues y comentarios.
- Notificaciones internas simples.
- Archivado y restauracion de proyectos/issues.
- Paginacion global para listas.
- Configuracion por `.env`.
- Documentacion de endpoints para Flutter.

## Stack

- Python 3.12
- Django 6
- Django REST Framework
- Simple JWT
- PostgreSQL
- django-cors-headers
- Pillow para imagenes
- psycopg para PostgreSQL

## Apps Principales

```text
users       Identidad global y autenticacion
workspaces  Equipos, membresias, roles y codigos de invitacion
projects    Proyectos dentro de un workspace
issues      Issues, comentarios, imagenes y notificaciones
config      Settings, rutas globales y configuracion del proyecto
```

## Modelo General

```text
User
  |
  | WorkspaceMembership role=owner/manager/developer/qa
  v
Workspace
  |
  v
Project
  |
  v
Issue
  |
  +-- Comment
  +-- IssueImage
  +-- Notification
```

Los roles no viven en el usuario global. Un mismo usuario puede ser QA en un workspace y owner en otro.

## Requisitos Para Ejecutar

Instala en la maquina:

- Python 3.12 o superior compatible con Django 6.
- PostgreSQL local.
- Git.

Dependencias Python del proyecto:

```bash
pip install -r requirements.txt
```

El archivo [requirements.txt](requirements.txt) contiene:

```text
asgiref
Django
django-cors-headers
djangorestframework
djangorestframework_simplejwt
pillow
psycopg
psycopg-binary
PyJWT
sqlparse
typing_extensions
```

## Instalacion Desde Cero

Clona el repositorio:

```bash
git clone https://github.com/david0909m/buglitch_backend.git
cd buglitch_backend
```

Crea y activa un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

Crea el archivo `.env` desde el ejemplo:

```bash
cp .env.example .env
```

Edita `.env` con tus datos locales:

```text
SECRET_KEY=change-me-in-env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=buglitch_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

El proyecto carga automaticamente `.env` desde `config/settings.py`, asi que no necesitas exportar variables manualmente para desarrollo local.

## Configurar PostgreSQL

En PostgreSQL crea una base de datos con el mismo nombre configurado en `.env`.

Ejemplo usando `psql`:

```bash
createdb buglitch_db
```

Si usas otro usuario o password, ajusta:

```text
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

## Migraciones

Ejecuta:

```bash
python manage.py migrate
```

Opcional: crea un superusuario para Django Admin:

```bash
python manage.py createsuperuser
```

## Ejecutar el Servidor

Para desarrollo web local:

```bash
python manage.py runserver
```

Para probar desde Flutter en emulador/dispositivo:

```bash
python manage.py runserver 0.0.0.0:8000
```

URLs base comunes:

```text
Local browser:     http://127.0.0.1:8000
Android emulator:  http://10.0.2.2:8000
iOS simulator:     http://127.0.0.1:8000
```

## Archivos Media

Las imagenes subidas a issues y comentarios se guardan localmente en:

```text
media/
```

En desarrollo Django sirve estos archivos mediante:

```text
/media/
```

Para produccion, los archivos media deberian servirse desde almacenamiento externo o un servidor dedicado.

## Autenticacion

Login:

```text
POST /api/token/
```

Refresh token:

```text
POST /api/token/refresh/
```

Registro con tokens:

```text
POST /api/users/register/
```

Usuario actual:

```text
GET /api/users/me/
```

Todas las rutas privadas usan:

```text
Authorization: Bearer <access_token>
```

## Endpoints Principales

### Workspaces

```text
GET    /api/workspaces/
POST   /api/workspaces/
GET    /api/workspaces/{id}/my_role/
GET    /api/workspaces/{id}/members/
POST   /api/workspaces/{id}/add_member/
POST   /api/workspaces/{id}/update_member_role/
POST   /api/workspaces/{id}/remove_member/
POST   /api/workspaces/{id}/invite-code/
GET    /api/workspaces/{id}/invite-codes/
POST   /api/workspaces/join/
```

Join por codigo:

```json
{
  "code": "BUG-8F3K2A"
}
```

### Projects

```text
GET    /api/projects/?workspace=1
POST   /api/projects/
PATCH  /api/projects/{id}/
DELETE /api/projects/{id}/
PATCH  /api/projects/{id}/archive/
PATCH  /api/projects/{id}/restore/
```

`DELETE` archiva el proyecto, no lo elimina permanentemente.

### Issues

```text
GET    /api/issues/?project=1
GET    /api/issues/?project=1&status=todo
GET    /api/issues/?project=1&priority=high
GET    /api/issues/?project=1&assignee=2
GET    /api/issues/?project=1&search=login
POST   /api/issues/
PATCH  /api/issues/{id}/assign/
PATCH  /api/issues/{id}/update_status/
POST   /api/issues/{id}/upload_image/
PATCH  /api/issues/{id}/archive/
PATCH  /api/issues/{id}/restore/
```

Para crear un issue con imagenes se usa `multipart/form-data` con campos repetidos `images`.

### Comentarios

```text
GET  /api/issues/{id}/comments/
POST /api/issues/{id}/comments/
```

Tambien soporta `multipart/form-data` para comentar con imagenes:

```text
content=Error reproducido en Android
images=<file1>
images=<file2>
```

### Notificaciones

```text
GET   /api/notifications/
GET   /api/notifications/?is_read=false
PATCH /api/notifications/{id}/mark_read/
PATCH /api/notifications/mark_all_read/
```

Modelo de notificacion MVP:

```text
user
title
message
type
is_read
created_at
```

## Roles y Permisos

```text
owner      Administra workspace, owners, miembros, proyectos e issues.
manager    Administra miembros no-owner, proyectos e issues.
developer  Puede trabajar issues asignados y cambiar status si es su issue.
qa         Puede crear issues, comentar y adjuntar evidencias.
```

Reglas importantes:

- El ultimo owner no puede ser removido ni degradado.
- Solo owner puede crear o modificar otro owner.
- Solo owner/manager puede crear proyectos.
- Solo owner/manager puede asignar issues.
- Developer puede mover status solo si el issue esta asignado a el.
- Cualquier miembro del workspace puede comentar y subir imagenes.

## Paginacion

Las listas devuelven este formato:

```json
{
  "count": 30,
  "next": "http://127.0.0.1:8000/api/issues/?page=2",
  "previous": null,
  "results": []
}
```

En Flutter se debe consumir `results`.

## Documentacion Para Flutter

La guia de consumo para Flutter esta en:

- [FLUTTER_ENDPOINTS.md](FLUTTER_ENDPOINTS.md)

Tambien hay una guia rapida de pruebas:

- [API_TESTING.md](API_TESTING.md)

## Comandos Utiles

Verificar configuracion Django:

```bash
python manage.py check
```

Crear migraciones:

```bash
python manage.py makemigrations
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Ejecutar servidor:

```bash
python manage.py runserver 0.0.0.0:8000
```

## Notas de Seguridad

- `.env` no se sube al repositorio.
- `.env.example` solo contiene valores de ejemplo.
- `SECRET_KEY`, credenciales de base de datos y configuracion de hosts deben cambiarse en cada entorno.
- `DEBUG=True` es solo para desarrollo.
- Para produccion se debe configurar almacenamiento media, CORS y `ALLOWED_HOSTS` de forma estricta.
