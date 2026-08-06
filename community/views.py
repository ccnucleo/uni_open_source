from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from projects.models import Project

@login_required(login_url="accounts:login")
def community_list_view(request):
    # Traemos a todos los usuarios activos, excluyendo a los administradores
    # y (opcionalmente) te excluimos a ti mismo de la lista pública
    developers = User.objects.filter(is_active=True, is_superuser=False).exclude(id=request.user.id)
    
    return render(
        request, 
        "web/pages/community/community_page.html", 
        {
            "active_section": "community", # Para que el Sidebar se pinte de naranja
            "page_title": "Comunidad de Desarrolladores",
            "developers": developers
        }
    )

from django.db.models import Q

@login_required(login_url="accounts:login")
def community_profile_view(request, username):
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