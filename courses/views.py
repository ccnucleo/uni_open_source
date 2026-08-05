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
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('categoria', '').strip()
    selected_levels = request.GET.getlist('nivel')
    selected_tag_ids = request.GET.getlist('tag')

    courses = Course.objects.select_related('category').prefetch_related('tags').all()

    if query:
        courses = courses.filter(title__icontains=query)

    if category_id:
        courses = courses.filter(category_id=category_id)

    if selected_levels:
        courses = courses.filter(level__in=selected_levels)

    if selected_tag_ids:
        courses = courses.filter(tags__id__in=selected_tag_ids).distinct()

    paginator = Paginator(courses, COURSES_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Querystring sin el parámetro "page", para poder pegarle &page=N
    # a cada link de paginación sin perder los filtros activos.
    querystring = request.GET.copy()
    querystring.pop('page', None)

    context = {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
        'categories': Category.objects.all().order_by('name'),
        'tags': Tag.objects.all().order_by('name'),
        'levels': Course.LEVEL_CHOICES,
        'query': query,
        'selected_category_id': category_id,
        'selected_levels': selected_levels,
        'selected_tag_ids': selected_tag_ids,
        'querystring': querystring.urlencode(),
    }
    return render(request, 'web/pages/courses/courses_page.html', context)


@login_required(login_url="accounts:login")
def course_detail_page(request, course_id):
	course = get_object_or_404(Course.objects.select_related("owner"), pk=course_id)
	return render(
		request,
		"web/pages/courses/course_detail.html",
		{
			"course": course,
			"active_section": "courses",
			"page_title": course.title,
		},
	)


def _parse_json_body(request):
	try:
		return json.loads(request.body.decode("utf-8"))
	except (json.JSONDecodeError, UnicodeDecodeError):
		return None


def _serialize_course(course):
	return {
		"id": course.id,
		"title": course.title,
		"short_description": course.short_description,
		"description": course.description,
		"category": course.category,
		"level": course.level,
		"owner": course.owner.username,
		"is_published": course.is_published,
		"created_at": course.created_at.isoformat(),
		"updated_at": course.updated_at.isoformat(),
	}


@login_required(login_url="accounts:login")
@require_http_methods(["GET", "POST"])
def courses_collection_api(request):
	if request.method == "GET":
		items = [_serialize_course(c) for c in Course.objects.select_related("owner").all()]
		return JsonResponse({"success": True, "data": items})

	if not request.user.is_authenticated:
		return JsonResponse(
			{"success": False, "message": "Autenticacion requerida."},
			status=401,
		)

	payload = _parse_json_body(request)
	if payload is None:
		return JsonResponse(
			{"success": False, "message": "JSON invalido."},
			status=400,
		)

	title = (payload.get("title") or "").strip()
	if not title:
		return JsonResponse(
			{"success": False, "message": "El titulo es obligatorio."},
			status=400,
		)

	course = Course.objects.create(
		title=title,
		short_description=(payload.get("short_description") or "").strip(),
		description=(payload.get("description") or "").strip(),
		category=(payload.get("category") or "").strip(),
		level=(payload.get("level") or Course.BEGINNER).strip() or Course.BEGINNER,
		owner=request.user,
		is_published=bool(payload.get("is_published", False)),
	)
	return JsonResponse({"success": True, "data": _serialize_course(course)}, status=201)


@login_required(login_url="accounts:login")
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def courses_item_api(request, course_id):
	try:
		course = Course.objects.select_related("owner").get(pk=course_id)
	except Course.DoesNotExist as exc:
		raise Http404("Course not found") from exc

	if request.method == "GET":
		return JsonResponse({"success": True, "data": _serialize_course(course)})

	if not request.user.is_authenticated:
		return JsonResponse(
			{"success": False, "message": "Autenticacion requerida."},
			status=401,
		)

	if course.owner_id != request.user.id:
		return JsonResponse(
			{"success": False, "message": "No tienes permisos sobre este curso."},
			status=403,
		)

	if request.method == "DELETE":
		course.delete()
		return JsonResponse({"success": True, "message": "Curso eliminado."})

	payload = _parse_json_body(request)
	if payload is None:
		return JsonResponse(
			{"success": False, "message": "JSON invalido."},
			status=400,
		)

	for field in ["title", "short_description", "description", "category", "level"]:
		if field in payload:
			value = payload.get(field)
			setattr(course, field, (value or "").strip() if isinstance(value, str) else value)

	if "is_published" in payload:
		course.is_published = bool(payload.get("is_published"))

	if course.level not in {choice[0] for choice in Course.LEVEL_CHOICES}:
		return JsonResponse(
			{"success": False, "message": "Nivel no valido."},
			status=400,
		)

	if not course.title:
		return JsonResponse(
			{"success": False, "message": "El titulo es obligatorio."},
			status=400,
		)

	course.save()
	return JsonResponse({"success": True, "data": _serialize_course(course)})