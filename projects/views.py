import json
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from .models import Project


def projects_page(request):
	projects = Project.objects.select_related("owner").all()[:24]
	return render(
		request,
		"web/pages/projects/projects_page.html",
		{
			"projects": projects,
			"active_section": "projects",
			"page_title": "Proyectos",
		},
	)


def project_detail_page(request, project_id):
	project = get_object_or_404(Project.objects.select_related("owner"), pk=project_id)
	return render(
		request,
		"web/pages/projects/project_detail.html",
		{
			"project": project,
			"active_section": "projects",
			"page_title": project.title,
		},
	)


def _parse_payload(request):
	if request.content_type == "application/json" or (request.body and not request.POST):
		try:
			return json.loads(request.body.decode("utf-8"))
		except (json.JSONDecodeError, UnicodeDecodeError):
			return None
	if request.POST:
		return dict(request.POST.items())
	return {}


def _serialize_project(project):
	return {
		"id": project.id,
		"title": project.title,
		"summary": project.summary,
		"description": project.description,
		"theme": project.theme,
		"theme_display": project.get_theme_display(),
		"tech_stack": project.tech_stack,
		"main_tech": project.main_tech,
		"image_url": project.image_url,
		"repository_url": project.repository_url,
		"demo_url": project.demo_url,
		"owner": project.owner.username,
		"owner_id": project.owner_id,
		"is_public": project.is_public,
		"created_at": project.created_at.isoformat() if project.created_at else None,
		"updated_at": project.updated_at.isoformat() if project.updated_at else None,
	}


@require_http_methods(["GET", "POST"])
def projects_collection_api(request):
	if request.method == "GET":
		items = [_serialize_project(p) for p in Project.objects.select_related("owner").all()]
		return JsonResponse({"success": True, "data": items})

	if not request.user.is_authenticated:
		return JsonResponse(
			{"success": False, "message": "Autenticacion requerida."},
			status=401,
		)

	payload = _parse_payload(request)
	if payload is None:
		return JsonResponse(
			{"success": False, "message": "JSON invalido."},
			status=400,
		)

	title = (payload.get("title") or payload.get("name") or "").strip()
	if not title:
		return JsonResponse(
			{"success": False, "message": "El titulo es obligatorio."},
			status=400,
		)

	summary = (payload.get("summary") or payload.get("desc") or "").strip()
	description = (payload.get("description") or payload.get("desc") or "").strip()
	main_tech = (payload.get("main_tech") or payload.get("tech_stack") or payload.get("tech") or "").strip()
	theme = (payload.get("theme") or "web").strip()
	repository_url = (payload.get("repository_url") or payload.get("repo_url") or "").strip()
	p1 = (payload.get("paragraph_1") or payload.get("p1") or description).strip()
	p2 = (payload.get("paragraph_2") or payload.get("p2") or "").strip()
	p3 = (payload.get("paragraph_3") or payload.get("p3") or "").strip()

	if not summary and description:
		summary = description[:255]

	project = Project(
		title=title,
		summary=summary,
		paragraph_1=p1,
		paragraph_2=p2,
		paragraph_3=p3,
		theme=theme,
		main_tech=main_tech,
		repository_url=repository_url,
		owner=request.user,
		is_public=bool(payload.get("is_public", True)),
	)

	image_file = request.FILES.get("image") or request.FILES.get("cover_image")
	if image_file:
		project.image = image_file

	project.save()

	return JsonResponse({"success": True, "data": _serialize_project(project)}, status=201)


@require_http_methods(["GET", "PUT", "PATCH", "POST", "DELETE"])
def projects_item_api(request, project_id):
	try:
		project = Project.objects.select_related("owner").get(pk=project_id)
	except Project.DoesNotExist as exc:
		raise Http404("Project not found") from exc

	if request.method == "GET":
		return JsonResponse({"success": True, "data": _serialize_project(project)})

	if not request.user.is_authenticated:
		return JsonResponse(
			{"success": False, "message": "Autenticacion requerida."},
			status=401,
		)

	if project.owner_id != request.user.id:
		return JsonResponse(
			{"success": False, "message": "No tienes permisos sobre este proyecto."},
			status=403,
		)

	if request.method == "DELETE":
		project.delete()
		return JsonResponse({"success": True, "message": "Proyecto eliminado."})

	payload = _parse_payload(request)
	if payload is None:
		return JsonResponse(
			{"success": False, "message": "Payload invalido."},
			status=400,
		)

	if "title" in payload or "name" in payload:
		title_val = (payload.get("title") or payload.get("name") or "").strip()
		if title_val:
			project.title = title_val
	if "summary" in payload:
		project.summary = (payload.get("summary") or "").strip()
	if "description" in payload or "desc" in payload:
		project.paragraph_1 = (payload.get("description") or payload.get("desc") or "").strip()
		if not project.summary:
			project.summary = project.paragraph_1[:255]
	if "tech_stack" in payload or "main_tech" in payload or "tech" in payload:
		project.main_tech = (payload.get("tech_stack") or payload.get("main_tech") or payload.get("tech") or "").strip()
	if "theme" in payload:
		project.theme = payload.get("theme") or "web"
	if "repository_url" in payload or "repo_url" in payload:
		project.repository_url = (payload.get("repository_url") or payload.get("repo_url") or "").strip()
	if "paragraph_1" in payload or "p1" in payload:
		project.paragraph_1 = (payload.get("paragraph_1") or payload.get("p1") or "").strip()
	if "paragraph_2" in payload or "p2" in payload:
		project.paragraph_2 = (payload.get("paragraph_2") or payload.get("p2") or "").strip()
	if "paragraph_3" in payload or "p3" in payload:
		project.paragraph_3 = (payload.get("paragraph_3") or payload.get("p3") or "").strip()
	if "is_public" in payload:
		project.is_public = bool(payload.get("is_public"))

	image_file = request.FILES.get("image") or request.FILES.get("cover_image")
	if image_file:
		project.image = image_file

	if not project.title:
		return JsonResponse(
			{"success": False, "message": "El titulo es obligatorio."},
			status=400,
		)

	project.save()
	return JsonResponse({"success": True, "data": _serialize_project(project)})

