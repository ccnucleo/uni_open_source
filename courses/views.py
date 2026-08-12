import json
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Course, Category, Tag

COURSES_PER_PAGE = 9

@login_required(login_url="accounts:login")
def courses_page(request):
    """
    Renderiza el catálogo de cursos con soporte para paginación y filtros múltiples.
    """
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('categoria', '').strip()
    selected_levels = request.GET.getlist('nivel')
    selected_tag_ids = request.GET.getlist('tag')

    courses = Course.objects.select_related('category').prefetch_related('tags').all()

    # Aplicación de filtros
    if query:
        courses = courses.filter(title__icontains=query)
    if category_id:
        courses = courses.filter(category_id=category_id)
    if selected_levels:
        courses = courses.filter(level__in=selected_levels)
    if selected_tag_ids:
        courses = courses.filter(tags__id__in=selected_tag_ids).distinct()

    # Paginación
    paginator = Paginator(courses, COURSES_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Persistencia de filtros en paginación
    querystring = request.GET.copy()
    querystring.pop('page', None)

    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.filter(course__isnull=False).distinct().order_by('name')

    context = {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
        'categories': categories,
        'tags': tags,
        'levels': Course.LEVEL_CHOICES,
        'query': query,
        'selected_category_id': category_id,
        'selected_levels': selected_levels,
        'selected_tag_ids': selected_tag_ids,
        'querystring': querystring.urlencode(),
    }
    return render(request, 'web/pages/courses/courses_page.html', context)

@login_required(login_url="accounts:login")
def course_detail_page(request, course_slug):
    """
    Renderiza la landing page de un curso específico utilizando su slug.
    Implementa get_object_or_404 para manejo seguro de registros inexistentes.
    """
    course = get_object_or_404(Course.objects.select_related("owner"), slug=course_slug)
    
    return render(
        request,
        "web/pages/courses/course_detail.html",
        {
            "course": course,
            "active_section": "courses",
            "page_title": course.title,
        },
    )

# ==========================================
# SECCIÓN API REST (Sin modificaciones requeridas)
# ==========================================

def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

def _resolve_category(cat_val):
    if not cat_val:
        return None
    if isinstance(cat_val, int) or (isinstance(cat_val, str) and cat_val.isdigit()):
        return Category.objects.filter(pk=int(cat_val)).first()
    if isinstance(cat_val, str) and cat_val.strip():
        cat_obj, _ = Category.objects.get_or_create(name=cat_val.strip())
        return cat_obj
    return None

def _serialize_course(course):
    return {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "short_description": course.short_description,
        "description": course.description,
        "category": course.category.name if course.category else None,
        "category_id": course.category.id if course.category else None,
        "level": course.level,
        "level_display": course.get_level_display(),
        "url": course.url,
        "resource_type": course.resource_type,
        "has_certification": course.has_certification,
        "image_url": course.image.url if course.image else None,
        "owner": course.owner.username,
        "is_published": course.is_published,
        "tags": [t.name for t in course.tags.all()],
        "created_at": course.created_at.isoformat(),
        "updated_at": course.updated_at.isoformat(),
    }

@login_required(login_url="accounts:login")
@require_http_methods(["GET", "POST"])
def courses_collection_api(request):
    if request.method == "GET":
        items = [_serialize_course(c) for c in Course.objects.select_related("owner", "category").prefetch_related("tags").all()]
        return JsonResponse({"success": True, "data": items})

    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Autenticación requerida."}, status=401)

    is_multipart = request.content_type.startswith('multipart/form-data')
    data = request.POST if is_multipart else (_parse_json_body(request) or {})
    files = request.FILES if is_multipart else {}

    title = str(data.get("title", "")).strip()
    if not title:
        return JsonResponse({"success": False, "message": "El título es obligatorio."}, status=400)

    cat_obj = _resolve_category(data.get("category"))
    level = str(data.get("level", Course.BEGINNER)).strip() or Course.BEGINNER
    if level not in {choice[0] for choice in Course.LEVEL_CHOICES}:
        level = Course.BEGINNER

    res_type = str(data.get("resource_type", Course.YOUTUBE)).strip() or Course.YOUTUBE
    if res_type not in {choice[0] for choice in Course.RESOURCE_CHOICES}:
        res_type = Course.YOUTUBE

    has_cert = str(data.get("has_certification", "")).lower() in ("true", "1", "on", "yes")

    course = Course.objects.create(
        title=title,
        short_description=str(data.get("short_description", "")).strip(),
        description=str(data.get("description", "")).strip(),
        category=cat_obj,
        level=level,
        url=str(data.get("url", "")).strip(),
        resource_type=res_type,
        has_certification=has_cert,
        owner=request.user,
        is_published=str(data.get("is_published", "true")).lower() in ("true", "1", "on", "yes"),
    )

    if "image" in files:
        course.image = files["image"]
        course.save()

    tag_str = str(data.get("tags", "")).strip()
    if tag_str:
        tag_names = [t.strip() for t in tag_str.split(",") if t.strip()]
        tag_objs = []
        for name in tag_names:
            tag_obj, _ = Tag.objects.get_or_create(name=name.lower())
            tag_objs.append(tag_obj)
        course.tags.set(tag_objs)

    return JsonResponse({"success": True, "message": "Curso creado exitosamente.", "data": _serialize_course(course)}, status=201)

@login_required(login_url="accounts:login")
@require_http_methods(["GET", "PUT", "PATCH", "DELETE", "POST"])
def courses_item_api(request, course_id):
    try:
        course = Course.objects.select_related("owner", "category").prefetch_related("tags").get(pk=course_id)
    except Course.DoesNotExist as exc:
        raise Http404("Course not found") from exc

    if request.method == "GET":
        return JsonResponse({"success": True, "data": _serialize_course(course)})

    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Autenticación requerida."}, status=401)

    if course.owner_id != request.user.id and not request.user.is_staff:
        return JsonResponse({"success": False, "message": "No tienes permisos sobre este curso."}, status=403)

    if request.method == "DELETE":
        course.delete()
        return JsonResponse({"success": True, "message": "Curso eliminado."})

    is_multipart = request.content_type.startswith('multipart/form-data')
    data = request.POST if is_multipart else (_parse_json_body(request) or {})
    files = request.FILES if is_multipart else {}

    valid_text_fields = ["title", "short_description", "description", "url", "level", "resource_type"]
    for field in valid_text_fields:
        if field in data:
            setattr(course, field, str(data.get(field)).strip())

    if "category" in data:
        course.category = _resolve_category(data.get("category"))

    if "has_certification" in data:
        course.has_certification = str(data.get("has_certification", "")).lower() in ("true", "1", "on", "yes")

    if "is_published" in data:
        course.is_published = str(data.get("is_published", "")).lower() in ("true", "1", "on", "yes")

    if "image" in files:
        course.image = files["image"]

    if course.level not in {choice[0] for choice in Course.LEVEL_CHOICES}:
        return JsonResponse({"success": False, "message": "Nivel no válido."}, status=400)

    if not course.title:
        return JsonResponse({"success": False, "message": "El título es obligatorio."}, status=400)

    from django.utils.text import slugify
    new_slug = slugify(course.title)
    if new_slug and Course.objects.filter(slug=new_slug).exclude(pk=course.pk).exists():
        new_slug = f"{new_slug}-{course.pk}"
    course.slug = new_slug

    course.save()

    if "tags" in data:
        tag_str = str(data.get("tags", "")).strip()
        tag_objs = []
        if tag_str:
            for name in [t.strip() for t in tag_str.split(",") if t.strip()]:
                tag_obj, _ = Tag.objects.get_or_create(name=name.lower())
                tag_objs.append(tag_obj)
        course.tags.set(tag_objs)

    return JsonResponse({"success": True, "message": "Curso actualizado.", "data": _serialize_course(course)})