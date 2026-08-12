# Análisis del Sistema UNI Open Source, Errores y Componentes Faltantes

Este documento presenta una auditoría técnica integral de la aplicación web **UNI Open Source**. El análisis abarca el funcionamiento general, la arquitectura de datos, los errores de programación (bugs), las partes desconectadas o faltantes y la evaluación de los datos requeridos frente a los mínimos necesarios para el sistema.

---

## 1. Funcionamiento General de la Web

**UNI Open Source** es una plataforma web orientada a comunidades universitarias de desarrollo de software. Su objetivo es permitir a los usuarios compartir proyectos de código abierto, acceder a cursos y rutas de aprendizaje, y conectar con otros desarrolladores.

### Arquitectura Técnica:
- **Backend:** Django 6.0 (Python).
- **Base de Datos:** SQLite (`db.sqlite3`).
- **Frontend:** HTML5 semántico, CSS3 Vanilla (con sistema de variables de diseño responsive), JavaScript Vanilla (`Fetch API`, `Cropper.js`, manipulación del DOM).
- **Sub-aplicaciones (Django Apps):**
  1. `core`: Configuración global del proyecto, URLs raíz y páginas institucionales.
  2. `accounts`: Registro con verificación por código de 6 dígitos, inicio de sesión, recuperación de contraseña, edición de perfil de usuario y ajustes.
  3. `projects`: Catálogo de proyectos open source, detalle de proyecto, subida de portadas/galería/documentos, interacción de "likes", conteo de vistas y filtrado avanzado.
  4. `courses`: Catálogo de cursos educativos clasificados por nivel, categoría y tecnologías, con detalle dinámico usando slugs.
  5. `community`: Directorio público de desarrolladores de la comunidad y vista de perfiles públicos.

---

## 2. Data que Utiliza el Aplicativo

El aplicativo gestiona datos a través de modelos relacionales en Django ORM, archivos fixtures en JSON y almacenamiento multimedia local.

### 2.1 Entidades y Modelos de Base de Datos:
- **`auth.User` (Django Core):** Identificación del usuario (`username`, `email`, `password`, `first_name`, `last_name`, `is_active`, `is_staff`).
- **`accounts.Profile`:** Perfil de usuario extendido (`bio`, `avatar`, `linkedin`, `github`, `contact_email`, relaciones ManyToMany con tecnologías e intereses).
- **`accounts.UnverifiedUser`:** Registro temporal pre-verificación (`username`, `email`, `password` hasheada, `verification_code`, `created_at`).
- **`projects.Project`:** Publicación de proyectos (`title`, `summary`, `description`, `image`, `documentation_file`, `repository_url`, `version`, `size`, `dependencies`, `views_count`, `owner`, `collaborators`, `likes`).
- **`projects.ProjectImage`:** Galería de imágenes secundarias de un proyecto (`image`, `order`).
- **`projects.Technology` & `projects.Tag`:** Tecnologías e insignias asignadas a los proyectos.
- **`courses.Course`:** Recurso educativo (`title`, `slug`, `short_description`, `description`, `category`, `tags`, `level`, `url`, `image`, `resource_type`, `has_certification`, `owner`, `is_published`).
- **`courses.Category` & `courses.Tag`:** Clasificación temática y tecnologías para los cursos.

### 2.2 Archivos de Datos Externos / Fixtures:
- **`cursos_prueba.json`:** Fixture JSON para inyectar categorías y cursos iniciales.
- **`usuarios_prueba.json`:** Fixture JSON con usuarios y perfiles ficticios para pruebas.
- **Carpeta `media/`:** Almacena imágenes subidas por usuarios (`profile_pics/`, `projects/covers/`, `projects/gallery/`, `courses/thumbnails/`, `projects/docs/`).
- **Carpeta `web/static/web/img/colaborators/`:** Inspeccionada dinámicamente en `index_view` para listar logos de aliados en la landing page.

---

## 3. Errores de Programación (Bugs Detectados)

| # | Ubicación | Descripción del Error | Impacto / Consecuencia |
|---|---|---|---|
| 1 | `courses/views.py`<br>(Líneas 123 y 158) | **Error de Tipo en API de Cursos:** En `courses_collection_api` y `courses_item_api`, se intenta asignar `category=(payload.get("category") or "").strip()`. Al ser `category` una `ForeignKey` a `Category`, asignar un string causa una excepción de tiempo de ejecución. | Crash servidor con `ValueError: Cannot assign "'...'": "Course.category" must be a "Category" instance.` al crear o editar un curso vía API. |
| 2 | `accounts/views.py`<br>(Líneas 195, 281, 312) | **Mismatch en Dirección del Emisor de Correo:** `send_mail` pasa `os.getenv("EMAIL_USER")` como remitente (`from_email`), pero en `core/settings.py` el usuario de SMTP configurado es `EMAIL_HOST_USER`. Si `.env` no define `EMAIL_USER`, la variable evaluará como `None`. | Fallo silencioso o rechazo por el servidor SMTP de Gmail durante el registro y recuperación de clave. |
| 3 | `core/settings.py`<br>(Líneas 140 y 143) | **Credenciales Sensibles Expuestas:** Contraseña de aplicación de Gmail hardcodeda directamente en el código base en lugar de cargarse exclusivamente desde `.env`. | Riesgo grave de seguridad y fuga de credenciales en control de versiones. |
| 4 | `accounts/models.py`<br>vs `projects/models.py` | **Modelos Duplicados e Desconectados:** `accounts` define `Technology` (campo `nombre`) y `projects` define `Technology` (campo `name`). Ocurre lo mismo con `Tag` en `projects` y `courses`. | Creación de tablas duplicadas en la BD (`accounts_technology` vs `projects_technology`). Las tecnologías del perfil de usuario no concuerdan ni interactúan con los filtros de proyectos. |
| 5 | `community/views.py`<br>(Línea 19) | **Cálculo Ineficiente/Erróneo de Proyectos en Comunidad:** Uso de `annotate(total_projects=Count('owned_projects', distinct=True) + Count('collaborated_projects', distinct=True))`. | En ciertos motores SQL de producción, la suma directa de agregaciones de dos `ManyToMany` causa conteos inflados o errores de agrupar por (`GROUP BY`). |
| 6 | `cursos_prueba.json` | **Fixtures Incompletos:** El JSON de prueba no incluye la clave `"slug"` para los objetos `courses.course`. | Si se ejecuta `loaddata`, los cursos quedan con `slug=null`, rompiendo las rutas dinámicas `/courses/<slug>/` de Django. |
| 7 | `courses/models.py`<br>(Líneas 26-32) | **Excepción en `save()` de `Tag`:** `Tag.clean()` lanza `ValidationError` si el nombre existe case-insensitivamente. El método `save()` llama a `clean()`, lo que detiene la ejecución del servidor si no se captura con un bloque `try-except` en la API. | Error HTTP 500 no controlado al intentar guardar un tag duplicado desde código o endpoints REST. |

---

## 4. Partes Faltantes y Componentes Desconectados

### 4.1 Desconexión Módulo de Cursos (Frontend vs Backend):
- **Falta Interfaz de Creación/Edición de Cursos:** Existen endpoints REST para la API de cursos (`courses_collection_api`, `courses_item_api`), pero **NO existe ningún modal, formulario HTML ni script JS** para que los usuarios o administradores puedan publicar o editar un curso desde el navegador. La única forma actual es mediante Django Admin o cliente HTTP externo.

### 4.2 App `community` Incompleta:
- **`community/models.py` está vacío (0 modelos):** La aplicación no tiene modelos propios. Carece de funcionalidades clave para una comunidad universitaria como:
  - Sistema de mensajes directos entre desarrolladores.
  - Solicitudes de colaboración o seguimiento (Follow system).
  - Publicaciones, anuncios o foros de discusión.

### 4.3 Elementos UI Desconectados (Links Rotos / Placeholders):
- **Pestañas de Ordenamiento en Perfil (`web/templates/web/pages/profile/profile.html`):** Los enlaces de ordenamiento de proyectos ("Más recientes", "Más antiguos", "A-Z", "Z-A") tienen `href="#"` y no poseen eventos en JS (`scripts.js`) que ordenen dinámicamente las tarjetas de proyectos del usuario.
- **Acciones en Perfil Público de Comunidad (`community_profile.html`):** Los botones para contactar o interactuar con el desarrollador sólo usan un enlace estático `mailto:`, el cual falla si el usuario no especificó un correo de contacto o si no tiene cliente de correo instalado.

---

## 5. Errores en Datos Pedidos vs. Mínimos Necesarios

| Formulario / Módulo | Datos Solicitados Actualmente | Datos Mínimos Necesarios | Inconsistencias o Fallas Identificadas |
|---|---|---|---|
| **Registro de Usuario** | Username, Email, Password, First Name (mín 3 letras), Last Name (mín 3 letras). | Username, Email, Password. | Exigir obligatoriamente Nombre y Apellidos de mínimo 3 letras en el registro frena la conversión de usuarios. Además, usuarios importados por fixtures o creados desde el admin sin estos datos rompen el estándar en la UI. |
| **Perfil de Usuario** | Bio, Avatar, LinkedIn, GitHub, Email de contacto, Tecnologías, Intereses. | Username, Email. | En `update_profile_api`, si el usuario deja vacíos los campos de contacto, el backend le asigna automáticamente `user.email` a `contact_email`, exponiendo involuntariamente su correo principal privado. |
| **Creación de Proyectos** | Título (mín 3), Resumen (mín 10), Descripción, Portada, Doc PDF, Repositorio URL, Versión, Tamaño, Dependencias, Tecnologías, Tags, Colaboradores. | Título, Resumen, Repositorio/Demostración, Al menos 1 Tecnología. | - Campos como `version` tienen hardcoded `"v1.0.0"`.<br>- `size` es un texto libre ("15 MB") sin validación de formato ni bytes.<br>- `dependencies` es un bloque de texto sin formato estandarizado (ej. requirements.txt / package.json). |
| **Publicación de Cursos** | Título, Slug, Short Description, Description, Categoría, Tags, Nivel, URL, Imagen, Tipo de Recurso, Certificación. | Título, Categoría, Nivel, URL oficial. | `short_description` y `description` son opcionales (`blank=True`). Si un curso no tiene descripción corta, la tarjeta pública se renderiza vacía en el catálogo. |

---

## 6. Anotación Consolidada de Todo lo Faltante (Roadmap de Trabajo)

Para completar y estabilizar el sistema **UNI Open Source**, se requiere abordar las siguientes tareas prioritarias:

### 1. Corrección de Bugs Críticos en Backend:
- [ ] Corregir la asignación de `Category` en `courses/views.py` (obtener la instancia de `Category` por ID o nombre antes de guardar el modelo `Course`).
- [ ] Unificar las credenciales de correo configurando `EMAIL_HOST_USER` en `accounts/views.py` y moviendo la clave de aplicación de Gmail a `.env`.
- [ ] Refactorizar la agregación de `total_projects` en `community/views.py` utilizando subconsultas (`Subquery` / `OuterRef`).
- [ ] Agregar el campo `"slug"` a todos los registros del archivo fixture `cursos_prueba.json`.

### 2. Unificación del Esquema de Datos (Refactor de Modelos):
- [ ] Unificar los modelos `Technology` y `Tag` en una app compartida (o centralizarlos en `core` o `projects`), migrando las referencias en `accounts` y `courses`.

### 3. Conexión de Funcionalidades Frontend Desconectadas:
- [ ] Diseñar e implementar el modal y la lógica JS para que los usuarios puedan **Publicar / Editar Cursos** desde la interfaz web.
- [ ] Conectar los manejadores de eventos JS en `scripts.js` para los botones de ordenamiento (`data-sort`) en la vista de perfil de usuario.
- [ ] Desarrollar modelos en `community/models.py` (ej. `DeveloperConnection` o `Message`) para habilitar la interacción real entre desarrolladores.

### 4. Ajustes en Validaciones y Experiencia de Usuario (UX):
- [ ] Permitir el registro con datos opcionales en `first_name` y `last_name`, o ajustar las validaciones para aceptar nombres de 2 letras.
- [ ] Modificar `update_profile_api` para no sobreescribir `contact_email` con el correo privado del usuario a menos que este lo solicite explícitamente.
- [ ] Estandarizar los campos `dependencies` y `size` en los proyectos con validadores adecuados.
