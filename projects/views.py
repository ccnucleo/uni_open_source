import json
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .models import Project, ProjectImage, Tag, Technology

User = get_user_model()

def projects_page(request):
    # 1. Obtener parámetros de la URL enviados por el formulario
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'recent')
    theme = request.GET.get('theme', '').strip()
    tech = request.GET.get('tech', '').strip()
    author = request.GET.get('author', '').strip()
    
    # Parámetros de rango de fecha
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # 2. QuerySet base optimizado para evitar N+1 (incluye perfil del autor)
    projects = (
        Project.objects.filter(is_public=True)
        .select_related("owner", "owner__profile")
        .prefetch_related("technologies", "tags")
        .annotate(likes_count=Count('likes', distinct=True))
    )

    # 3. Aplicar Filtros dinámicos
    if q:
        projects = projects.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(description__icontains=q))
    if theme:
        projects = projects.filter(tags__name__iexact=theme)
    if tech:
        projects = projects.filter(technologies__name__iexact=tech)
    if author:
        projects = projects.filter(owner__username__icontains=author)
    if date_from:
        projects = projects.filter(created_at__date__gte=date_from)
    if date_to:
        projects = projects.filter(created_at__date__lte=date_to)

    # 4. Eliminar duplicados
    projects = projects.distinct()

    # 5. Aplicar Ordenamiento
    if sort == 'popular':
        projects = projects.order_by('-likes_count', '-created_at')
    elif sort == 'views':
        projects = projects.order_by('-views_count', '-created_at')
    elif sort == 'az':
        projects = projects.order_by('title')
    else: # Por defecto: más recientes
        projects = projects.order_by('-created_at')

    # Limitamos los resultados para rendimiento óptimo
    projects = projects[:24]

    # Extraemos filtros predictivos optimizados (distinct para no enviar duplicados)
    all_tags = list(Tag.objects.values_list('name', flat=True).distinct()[:40])
    all_techs = list(Technology.objects.values_list('name', flat=True).distinct()[:40])
    all_authors = list(User.objects.filter(owned_projects__isnull=False).values_list('username', flat=True).distinct()[:40])

    return render(
        request, 
        "web/pages/projects/projects_page.html", 
        {
            "projects": projects, 
            "active_section": "projects",
            "page_title": "Proyectos",
            "all_tags": all_tags,
            "all_techs": all_techs,
            "all_authors": all_authors,
        }
    )


def project_detail_page(request, project_id):
    project = get_object_or_404(Project.objects.select_related("owner").prefetch_related('gallery', 'collaborators', 'likes', 'tags', 'technologies'), pk=project_id)
    project.views_count += 1
    project.save(update_fields=['views_count'])

    all_tags = list(Tag.objects.values_list('name', flat=True))
    all_techs = list(Technology.objects.values_list('name', flat=True))
    all_users = list(User.objects.exclude(id=project.owner.id).values_list('username', flat=True))

    return render(
        request,
        "web/pages/projects/project_detail.html",
        {
            "project": project,
            "all_tags": json.dumps(all_tags),
            "all_techs": json.dumps(all_techs),
            "all_users": json.dumps(all_users),
            "active_section": "projects",
            "page_title": "Proyectos", 
        },
    )

def _parse_json_body(request):
    try: return json.loads(request.body.decode("utf-8"))
    except: return None

@require_http_methods(["POST"])
def toggle_like_api(request, project_id):
    if not request.user.is_authenticated: return JsonResponse({"success": False, "message": "Debes iniciar sesión."}, status=401)
    project = get_object_or_404(Project, pk=project_id)
    if request.user in project.likes.all():
        project.likes.remove(request.user)
        return JsonResponse({"success": True, "liked": False, "likes_count": project.likes.count()})
    else:
        project.likes.add(request.user)
        return JsonResponse({"success": True, "liked": True, "likes_count": project.likes.count()})

@require_http_methods(["GET", "POST"])
def projects_collection_api(request):
    if not request.user.is_authenticated: return JsonResponse({"success": False, "message": "Autenticación requerida."}, status=401)
    
    if request.method == "GET":
        projects = Project.objects.filter(is_public=True).select_related("owner").order_by("-created_at")[:24]
        data = [
            {
                "id": p.id,
                "title": p.title,
                "summary": p.summary,
                "owner": p.owner.username,
                "created_at": p.created_at.isoformat(),
            }
            for p in projects
        ]
        return JsonResponse({"success": True, "data": data})

    is_multipart = request.content_type.startswith('multipart/form-data')
    data = request.POST if is_multipart else (_parse_json_body(request) or {})
    files = request.FILES if is_multipart else {}

    title = str(data.get("title", "")).strip()
    summary = str(data.get("summary", "")).strip()
    image = files.get("image")

    if len(title) < 3 or len(summary) < 10: 
        return JsonResponse({"success": False, "message": "El título debe tener al menos 3 caracteres y el resumen 10."}, status=400)

    tech_names = [t.strip() for t in str(data.get("technologies", "")).split(",") if t.strip()]
    tag_names = [t.strip().lower() for t in str(data.get("tags", "")).split(",") if t.strip()]

    if not tech_names and not tag_names:
        return JsonResponse({"success": False, "message": "Debes añadir al menos una tecnología o etiqueta."}, status=400)

    project = Project.objects.create(title=title, summary=summary, image=image, owner=request.user, is_public=True)

    if tech_names:
        tech_objs = []
        for name in tech_names:
            tech = Technology.objects.filter(name__iexact=name).first()
            if not tech:
                tech = Technology.objects.create(name=name)
            tech_objs.append(tech)
        project.technologies.set(tech_objs)

    if tag_names:
        tag_objs = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        project.tags.set(tag_objs)

    collab_names = [u.strip() for u in str(data.get("collaborators", "")).split(",") if u.strip()]
    if collab_names:
        users = User.objects.filter(username__in=collab_names).exclude(id=request.user.id)
        project.collaborators.set(users)

    return JsonResponse({"success": True, "message": "Proyecto creado exitosamente."})

@require_http_methods(["GET", "PUT", "PATCH", "DELETE", "POST"])
def projects_item_api(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not request.user.is_authenticated or project.owner_id != request.user.id:
        return JsonResponse({"success": False, "message": "No tienes permisos."}, status=403)

    if request.method == "DELETE":
        project.delete()
        return JsonResponse({"success": True, "message": "Proyecto eliminado."})

    is_multipart = request.content_type.startswith('multipart/form-data')
    data = request.POST if is_multipart else (_parse_json_body(request) or {})
    files = request.FILES if is_multipart else {}

    valid_text_fields = ["title", "summary", "description", "repository_url", "version", "size", "dependencies"]
    for field in valid_text_fields:
        if field in data: setattr(project, field, str(data.get(field)).strip())

    if "technologies" in data:
        tech_names = [t.strip() for t in str(data.get("technologies", "")).split(",") if t.strip()]
        tech_objs = []
        for name in tech_names:
            tech = Technology.objects.filter(name__iexact=name).first()
            if not tech:
                tech = Technology.objects.create(name=name)
            tech_objs.append(tech)
        project.technologies.set(tech_objs)

    if "tags" in data:
        tag_names = [t.strip().lower() for t in str(data.get("tags", "")).split(",") if t.strip()]
        tag_objs = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        project.tags.set(tag_objs)

    if "collaborators" in data:
        usernames = [u.strip() for u in str(data.get("collaborators", "")).split(",") if u.strip()]
        if usernames:
            users = User.objects.filter(username__in=usernames).exclude(id=project.owner.id)
            project.collaborators.set(users)
        else:
            project.collaborators.clear()

    if "image" in files: project.image = files["image"]
    if "documentation_file" in files: project.documentation_file = files["documentation_file"]

    project.save()

    if "gallery_images" in files:
        # Poner nuevas imágenes al final
        current_count = project.gallery.count()
        for i, img in enumerate(files.getlist("gallery_images")): 
            ProjectImage.objects.create(project=project, image=img, order=current_count + i)
            
    if "deleted_images" in data:
        del_ids = [i for i in data.get("deleted_images", "").split(",") if i.isdigit()]
        ProjectImage.objects.filter(id__in=del_ids, project=project).delete()

    if "image_order" in data:
        order_ids = [int(i) for i in str(data.get("image_order", "")).split(",") if i.isdigit()]
        for idx, img_id in enumerate(order_ids):
            ProjectImage.objects.filter(id=img_id, project=project).update(order=idx)

    return JsonResponse({"success": True, "message": "Proyecto actualizado."})
