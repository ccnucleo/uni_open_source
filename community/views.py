import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, OuterRef, Subquery, IntegerField, Value, Sum, F
from django.db.models.functions import Coalesce

from projects.models import Project
from .models import Follow, Message

@login_required(login_url="accounts:login")
def community_list_view(request):
    search_query = request.GET.get('search', '').strip()
    skill_query = request.GET.get('skill', '').strip()

    # Subconsultas seguras para evitar errores de conteo en la suma de ManyToMany
    owned_sub = Project.objects.filter(owner=OuterRef('pk')).values('owner').annotate(c=Count('id')).values('c')
    collab_sub = Project.objects.filter(collaborators=OuterRef('pk')).values('collaborators').annotate(c=Count('id')).values('c')

    developers = User.objects.filter(
        is_active=True, 
        is_superuser=False
    ).exclude(id=request.user.id).select_related('profile').prefetch_related('profile__tecnologias')\
    .annotate(
        owned_cnt=Coalesce(Subquery(owned_sub, output_field=IntegerField()), Value(0)),
        collab_cnt=Coalesce(Subquery(collab_sub, output_field=IntegerField()), Value(0))
    ).annotate(
        total_projects=F('owned_cnt') + F('collab_cnt')
    )

    if search_query:
        developers = developers.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if skill_query:
        developers = developers.filter(
            Q(profile__tecnologias__nombre__icontains=skill_query) |
            Q(profile__tecnologias__name__icontains=skill_query)
        )

    developers = developers.distinct().order_by('-date_joined', 'id')

    paginator = Paginator(developers, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request, 
        "web/pages/community/community_page.html", 
        {
            "active_section": "community",
            "page_title": "Comunidad de Desarrolladores",
            "page_obj": page_obj,
            "search_query": search_query,
            "skill_query": skill_query,
        }
    )

@login_required(login_url="accounts:login")
def community_profile_view(request, username):
    if request.user.username == username:
        return redirect('accounts:profile')
        
    public_user = get_object_or_404(User, username=username)
    
    public_projects = Project.objects.filter(
        Q(owner=public_user) | Q(collaborators=public_user)
    ).distinct().order_by('-created_at')
    
    followers_count = public_user.follower_relations.count()
    following_count = public_user.following_relations.count()
    total_views = public_projects.aggregate(total=Coalesce(Sum('views_count'), Value(0)))['total']
    
    is_following = Follow.objects.filter(follower=request.user, following=public_user).exists()
    
    return render(
        request, 
        "web/pages/community/community_profile.html", 
        {
            "active_section": "community", 
            "page_title": f"Perfil de {public_user.username}",
            "public_user": public_user,
            "public_projects": public_projects,
            "followers_count": followers_count,
            "following_count": following_count,
            "total_views": total_views,
            "is_following": is_following,
        }
    )

@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def toggle_follow_api(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        return JsonResponse({"success": False, "message": "No puedes seguirte a ti mismo."}, status=400)

    follow_obj = Follow.objects.filter(follower=request.user, following=target_user).first()
    if follow_obj:
        follow_obj.delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True

    followers_count = target_user.follower_relations.count()
    return JsonResponse({
        "success": True, 
        "is_following": is_following, 
        "followers_count": followers_count
    })

@login_required(login_url="accounts:login")
@require_http_methods(["POST"])
def send_message_api(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        return JsonResponse({"success": False, "message": "No puedes enviarte un mensaje a ti mismo."}, status=400)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else request.POST
    except Exception:
        data = request.POST

    subject = str(data.get("subject", "")).strip()
    body = str(data.get("body", "")).strip()

    if not body:
        return JsonResponse({"success": False, "message": "El mensaje no puede estar vacío."}, status=400)

    Message.objects.create(
        sender=request.user,
        recipient=target_user,
        subject=subject,
        body=body
    )

    return JsonResponse({"success": True, "message": "Mensaje enviado exitosamente."})