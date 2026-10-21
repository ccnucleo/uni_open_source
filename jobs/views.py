import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from courses.models import Career, Tag, Course
from .models import JobListing, JobBookmark

JOBS_PER_PAGE = 12

@login_required(login_url="accounts:login")
def jobs_page(request):
    """
    Renderiza el catálogo y recopilatorio de vacantes laborales con soporte para
    filtrado por especialidad de ingeniería, portal, modalidad, seniority y búsqueda textual.
    """
    query = request.GET.get('q', '').strip()
    career_code = request.GET.get('carrera', '').strip()
    selected_portal = request.GET.get('portal', '').strip()
    selected_modality = request.GET.get('modalidad', '').strip()
    selected_contract = request.GET.get('contrato', '').strip()
    selected_seniorities = request.GET.getlist('seniority')
    selected_tag_ids = request.GET.getlist('tag')

    jobs = (
        JobListing.objects
        .prefetch_related('careers', 'tags')
        .filter(status=JobListing.STATUS_ACTIVE)
    )

    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(company_name__icontains=query)
    if career_code:
        jobs = jobs.filter(careers__code=career_code)
    if selected_portal:
        jobs = jobs.filter(portal=selected_portal)
    if selected_modality:
        jobs = jobs.filter(modality=selected_modality)
    if selected_contract:
        jobs = jobs.filter(contract_type=selected_contract)
    if selected_seniorities:
        jobs = jobs.filter(seniority__in=selected_seniorities)
    if selected_tag_ids:
        jobs = jobs.filter(tags__id__in=selected_tag_ids).distinct()

    paginator = Paginator(jobs, JOBS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    querystring = request.GET.copy()
    querystring.pop('page', None)

    # Identificar qué vacantes han sido guardadas por el estudiante actual
    user_bookmarks_map = {}
    if request.user.is_authenticated:
        bookmarks = JobBookmark.objects.filter(user=request.user)
        user_bookmarks_map = {b.job_id: b.status for b in bookmarks}

    careers = Career.objects.all().order_by('order', 'name')
    tags = Tag.objects.filter(job_listings__isnull=False).distinct().order_by('name')[:30]

    context = {
        'page_obj': page_obj,
        'jobs': page_obj.object_list,
        'careers': careers,
        'tags': tags,
        'portals': JobListing.PORTAL_CHOICES,
        'modalities': JobListing.MODALITY_CHOICES,
        'contracts': JobListing.CONTRACT_CHOICES,
        'seniorities': JobListing.SENIORITY_CHOICES,
        'user_bookmarks_map': user_bookmarks_map,
        'query': query,
        'selected_career': career_code,
        'selected_portal': selected_portal,
        'selected_modality': selected_modality,
        'selected_contract': selected_contract,
        'selected_seniorities': selected_seniorities,
        'selected_tag_ids': selected_tag_ids,
        'querystring': querystring.urlencode(),
        'active_section': 'jobs',
        'page_title': 'Bolsa Laboral y Empleos',
    }
    return render(request, 'web/pages/jobs/jobs_page.html', context)


@login_required(login_url="accounts:login")
def job_detail_page(request, job_slug):
    """
    Renderiza la vista detallada de la vacante laboral, sus requisitos, enlace oficial
    de postulación y recomendaciones de cursos gratuitos para potenciar la postulación.
    """
    job = get_object_or_404(
        JobListing.objects.prefetch_related('careers', 'tags'),
        slug=job_slug
    )

    # Incrementar contador de vistas de manera atómica
    JobListing.objects.filter(pk=job.pk).update(views_count=job.views_count + 1)

    # Buscar estado de seguimiento del estudiante
    bookmark = JobBookmark.objects.filter(user=request.user, job=job).first()

    # Cursos afines para potenciar el perfil para esta vacante
    related_career_ids = job.careers.values_list('id', flat=True)
    recommended_courses = (
        Course.objects
        .filter(careers__id__in=related_career_ids, is_published=True)
        .distinct()
        .order_by('-last_synced_at')[:4]
    )

    context = {
        'job': job,
        'bookmark': bookmark,
        'recommended_courses': recommended_courses,
        'active_section': 'jobs',
        'page_title': f"{job.title} - {job.company_name}",
    }
    return render(request, 'web/pages/jobs/job_detail.html', context)


@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def toggle_bookmark_api(request, job_id):
    """
    Guarda o actualiza el estado de seguimiento de una vacante para el estudiante
    (guardado, postulado, en proceso, etc.).
    """
    job = get_object_or_404(JobListing, pk=job_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    action = data.get('action', 'toggle')
    new_status = data.get('status', JobBookmark.STATUS_SAVED)
    notes = data.get('notes', '')

    bookmark = JobBookmark.objects.filter(user=request.user, job=job).first()

    if action == 'remove' and bookmark:
        bookmark.delete()
        return JsonResponse({'success': True, 'bookmarked': False, 'status': None})

    if not bookmark:
        bookmark = JobBookmark.objects.create(
            user=request.user,
            job=job,
            status=new_status,
            notes=notes
        )
        return JsonResponse({'success': True, 'bookmarked': True, 'status': bookmark.status})
    else:
        if new_status:
            bookmark.status = new_status
        if notes:
            bookmark.notes = notes
        bookmark.save()
        return JsonResponse({'success': True, 'bookmarked': True, 'status': bookmark.status})


@login_required(login_url="accounts:login")
@require_http_methods(["GET"])
def jobs_collection_api(request):
    """API REST para consulta serializada de vacantes laborales."""
    jobs = JobListing.objects.filter(status=JobListing.STATUS_ACTIVE).prefetch_related('careers', 'tags')[:50]
    data = [
        {
            "id": j.id,
            "title": j.title,
            "slug": j.slug,
            "company_name": j.company_name,
            "portal": j.portal,
            "portal_display": j.get_portal_display(),
            "url": j.url,
            "country": j.country,
            "city": j.city,
            "modality": j.modality,
            "modality_display": j.get_modality_display(),
            "seniority": j.seniority,
            "seniority_display": j.get_seniority_display(),
            "contract_type": j.contract_type,
            "salary_display": j.salary_display,
            "short_description": j.short_description,
            "careers": [c.code for c in j.careers.all()],
            "tags": [t.name for t in j.tags.all()],
            "published_at": j.published_at.isoformat() if j.published_at else None,
        }
        for j in jobs
    ]
    return JsonResponse({"success": True, "data": data})
