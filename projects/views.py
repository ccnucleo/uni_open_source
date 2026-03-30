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


def _parse_json_body(request):
	try:
		return json.loads(request.body.decode("utf-8"))
	except (json.JSONDecodeError, UnicodeDecodeError):
		return None


def _serialize_project(project):
	return {
		"id": project.id,
		"title": project.title,
		"summary": project.summary,
		"description": project.description,
		"tech_stack": project.tech_stack,
		"repository_url": project.repository_url,
		"demo_url": project.demo_url,
		"owner": project.owner.username,
		"is_public": project.is_public,
		"created_at": project.created_at.isoformat(),
		"updated_at": project.updated_at.isoformat(),
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

	project = Project.objects.create(
		title=title,
		summary=(payload.get("summary") or "").strip(),
		description=(payload.get("description") or "").strip(),
		tech_stack=(payload.get("tech_stack") or "").strip(),
		repository_url=(payload.get("repository_url") or "").strip(),
		demo_url=(payload.get("demo_url") or "").strip(),
		owner=request.user,
		is_public=bool(payload.get("is_public", True)),
	)
	return JsonResponse({"success": True, "data": _serialize_project(project)}, status=201)


@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
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

	payload = _parse_json_body(request)
	if payload is None:
		return JsonResponse(
			{"success": False, "message": "JSON invalido."},
			status=400,
		)

	for field in ["title", "summary", "description", "tech_stack", "repository_url", "demo_url"]:
		if field in payload:
			value = payload.get(field)
			setattr(project, field, (value or "").strip() if isinstance(value, str) else value)

	if "is_public" in payload:
		project.is_public = bool(payload.get("is_public"))

	if not project.title:
		return JsonResponse(
			{"success": False, "message": "El titulo es obligatorio."},
			status=400,
		)

	project.save()
	return JsonResponse({"success": True, "data": _serialize_project(project)})
