from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from projects.models import Project
from django.core.paginator import Paginator
from django.db.models import Q, Count

@login_required(login_url="accounts:login")
def community_list_view(request):
    search_query = request.GET.get('search', '').strip()
    skill_query = request.GET.get('skill', '').strip()

    # Traemos a todos los usuarios activos, excluyendo a los administradores
    # y te excluimos a ti mismo de la lista pública
    developers = User.objects.filter(
        is_active=True, 
        is_superuser=False
    ).exclude(id=request.user.id).select_related('profile').prefetch_related('profile__tecnologias')\
    .annotate(total_projects=Count('owned_projects', distinct=True) + Count('collaborated_projects', distinct=True))

    if search_query:
        developers = developers.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if skill_query:
        developers = developers.filter(
            Q(profile__tecnologias__nombre__icontains=skill_query)
        )

    developers = developers.distinct().order_by('-date_joined', 'id')

    paginator = Paginator(developers, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request, 
        "web/pages/community/community_page.html", 
        {
            "active_section": "community", # Para que el Sidebar se pinte de naranja
            "page_title": "Comunidad de Desarrolladores",
            "page_obj": page_obj,
            "search_query": search_query,
            "skill_query": skill_query,
        }
    )

from django.db.models import Q

@login_required(login_url="accounts:login")
def community_profile_view(request, username):
    if request.user.username == username:
        return redirect('accounts:profile')
        
    # Buscamos al usuario por su nombre exacto, si no existe da error 404
    public_user = get_object_or_404(User, username=username)
    
    # Proyectos propios y en los que colabora
    public_projects = Project.objects.filter(Q(owner=public_user) | Q(collaborators=public_user)).distinct().order_by('-created_at')
    
    return render(
        request, 
        "web/pages/community/community_profile.html", 
        {
            "active_section": "community", 
            "page_title": f"Perfil de {public_user.username}",
            "public_user": public_user,
            "public_projects": public_projects
        }
    )