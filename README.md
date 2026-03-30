# UNI Open Source

Guia oficial para el equipo despues de la refactorizacion global.

## 1) Objetivo de esta nueva organizacion

El proyecto ahora separa de forma explicita:

- Logica de negocio por dominio (accounts, projects, courses).
- Capa visual compartida en web (layouts, componentes, paginas, css, js, img).

Resultado: podemos crecer en backend y frontend sin mezclar responsabilidades.

## 2) Arquitectura actual

### 2.1 Apps de negocio

- accounts: home/index, autenticacion, perfil, recuperacion de password, APIs de registro.
- projects: modelo, vistas HTML y APIs CRUD de proyectos.
- courses: modelo, vistas HTML y APIs CRUD de cursos.

### 2.2 Capa visual compartida

Toda la UI vive en web:

- Templates base y componentes:
	- web/templates/web/layouts/app_layout.html
	- web/templates/web/layouts/auth_layout.html
	- web/templates/web/components/topbar.html
	- web/templates/web/components/sidebar.html
	- web/templates/web/components/footer.html
- Paginas por dominio:
	- web/templates/web/pages/home/
	- web/templates/web/pages/auth/
	- web/templates/web/pages/profile/
	- web/templates/web/pages/projects/
	- web/templates/web/pages/courses/
- Assets globales:
	- web/static/web/css/
	- web/static/web/js/
	- web/static/web/img/

### 2.3 Enrutamiento

- core/urls.py registra ruta raiz (index), include de accounts, y rutas de projects/courses.
- accounts/urls.py concentra las rutas de auth/profile/reset/api con namespace accounts.

## 3) Convenciones obligatorias del proyecto

1. No crear templates ni static dentro de apps de negocio.
2. Toda pagina HTML nueva va en web/templates/web/pages/<dominio>/.
3. Todo CSS/JS/imagenes nuevo va en web/static/web/.
4. Views de negocio solo renderizan rutas web/pages/... y exponen API cuando aplique.
5. Cada app de negocio debe tener su urls.py propio y ser incluida desde core/urls.py.
6. Para paginas de app usar app_layout.html; para auth usar auth_layout.html.

## 4) Configuracion tecnica clave (ya aplicada)

En core/settings.py:

- Templates centralizados en web/templates.
- APP_DIRS = False.
- Loader de filesystem para evitar descubrimiento automatico en apps.
- Static globales en web/static.

Esto fuerza la disciplina de la nueva arquitectura.

## 5) Setup local

### 5.1 Requisitos

- Python 3.13+
- Virtual environment activo

### 5.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5.3 Validaciones basicas

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Nota: actualmente hay 0 tests, por lo que la validacion automatica es limitada.

### 5.4 Ejecutar servidor

```bash
python manage.py runserver
```

## 6) Como crear mas logica de negocio

Esta es la receta recomendada para un nuevo dominio, por ejemplo events.

### Paso 1: crear app

```bash
python manage.py startapp events
```

Agregar events en INSTALLED_APPS.

### Paso 2: modelar dominio

- Definir entidades en events/models.py.
- Registrar en events/admin.py si se administran desde Django Admin.

```bash
python manage.py makemigrations events
python manage.py migrate
```

### Paso 3: crear rutas de app

Crear events/urls.py con app_name y paths claros.

Ejemplo de patron:

```python
from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
		path("", views.events_page, name="list"),
		path("api/events/", views.events_collection_api, name="api_list_create"),
		path("api/events/<int:event_id>/", views.events_item_api, name="api_detail"),
		path("<int:event_id>/", views.event_detail_page, name="detail"),
]
```

### Paso 4: registrar rutas en core

En core/urls.py:

```python
path("events/", include("events.urls")),
```

### Paso 5: crear views

Separar claramente:

- View HTML de listado/detalle.
- API collection (GET/POST).
- API item (GET/PUT/PATCH/DELETE).

Usar JsonResponse con contrato consistente.

## 7) Como crear APIs nuevas

Checklist para APIs en cualquier app de dominio:

1. Definir URL versionable y clara (api/<recurso>/...).
2. Restringir metodos con require_http_methods.
3. Validar autenticacion para escritura.
4. Validar permisos de ownership cuando aplique.
5. Validar payload y devolver mensajes claros.
6. Responder siempre en JSON consistente:
	 - exito: {"success": true, "data": ...}
	 - error: {"success": false, "message": "..."}
7. Devolver status HTTP correcto (400, 401, 403, 404, 201, etc).

## 8) Como crear paginas HTML nuevas

### 8.1 Ubicacion

Crear archivos en:

- web/templates/web/pages/<dominio>/

Ejemplo:

- web/templates/web/pages/events/events_page.html
- web/templates/web/pages/events/event_detail.html

### 8.2 Heredar layout correcto

Para secciones internas de app:

```django
{% extends 'web/layouts/app_layout.html' %}
```

Para login/register/reset:

```django
{% extends 'web/layouts/auth_layout.html' %}
```

### 8.3 Contexto minimo recomendado en views

Pasar siempre en render:

- active_section: para marcar sidebar.
- page_title: para topbar.

Ejemplo:

```python
return render(
		request,
		"web/pages/events/events_page.html",
		{
				"active_section": "events",
				"page_title": "Eventos",
		},
)
```

## 9) Como crear CSS, JS e imagenes nuevas

### 9.1 Ubicacion

- CSS: web/static/web/css/
- JS: web/static/web/js/
- IMG: web/static/web/img/

### 9.2 Carga en templates

Usar siempre static:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'web/css/events.css' %}">
<script src="{% static 'web/js/events.js' %}"></script>
```

### 9.3 Regla de oro

No mover IDs o clases criticas del shell (topbar/sidebar/theme) sin actualizar el JS asociado.

## 10) Flujo de trabajo recomendado para nuevos features

1. Crear o ajustar modelo en app de dominio.
2. Crear/ajustar API en la misma app.
3. Crear pagina HTML en web/pages/<dominio>/.
4. Conectar view + URL.
5. Crear CSS/JS en web/static/web/.
6. Ejecutar validaciones:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

7. Hacer smoke test manual de rutas afectadas.

## 11) Estado de compatibilidad (importante)

- La app users fue eliminada.
- Las rutas de autenticacion/perfil operan desde accounts con namespace accounts.
- Nuevo desarrollo debe apuntar a accounts, projects, courses y web.

## 12) Checklist de Done por PR

Antes de abrir PR, verificar:

1. No se agregaron templates/static dentro de apps de negocio.
2. URLs registradas correctamente y names consistentes.
3. Permisos y autenticacion de APIs cubiertos.
4. check/makemigrations --check/test ejecutados.
5. Smoke test manual de flujo principal completado.
6. README actualizado si se introdujo una nueva convencion.

## 13) Notas de seguridad

- No commitear credenciales reales.
- Variables sensibles (correo, password, secretos) deben salir de codigo y venir por .env.
- Revisar periodicamente settings de seguridad para produccion (DEBUG, ALLOWED_HOSTS, CSRF, etc).

---

Si vas a crear una nueva linea de negocio, sigue el flujo de las secciones 6 a 10 como plantilla base.

