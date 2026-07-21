from django.core.management.base import BaseCommand
from courses.models import Category, Tag

class Command(BaseCommand):
    help = 'Inyecta la estructura profesional de Categorías y Etiquetas en la base de datos'

    def handle(self, *args, **kwargs):
        # 1. ÁREAS DE ESTUDIO (Categorías Principales)
        categorias = [
            "Fundamentos y Lógica",
            "Desarrollo Web (Frontend)",
            "Desarrollo Web (Backend)",
            "Bases de Datos y SQL",
            "Ciencia de Datos e IA",
            "Ciberseguridad y Redes",
            "DevOps y Cloud Computing",
            "Arquitectura de Software",
            "Full Stack",
            "Desarrollo Móvil",
            "Habilidades Blandas (Soft Skills)"
        ]

        # 2. HERRAMIENTAS Y LENGUAJES (Etiquetas / Tags)
        etiquetas = [
            # Lenguajes Core
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
            # Web
            "HTML/CSS", "React", "Angular", "Vue.js", "Node.js", "Django", "Spring Boot",
            # Datos
            "SQL Server", "MySQL", "PostgreSQL", "MongoDB", "Pandas", "Machine Learning", "Deep Learning",
            # Ciberseguridad & Infraestructura
            "Hacking Ético", "Criptografía", "Linux", "Docker", "Kubernetes", "AWS", "Git","Github", "Redes Cisco"
        ]

        self.stdout.write(self.style.WARNING('Iniciando el sembrado de datos...'))

        # Crear Categorías
        categorias_creadas = 0
        for cat_name in categorias:
            obj, created = Category.objects.get_or_create(name=cat_name)
            if created:
                categorias_creadas += 1

        # Crear Etiquetas
        etiquetas_creadas = 0
        for tag_name in etiquetas:
            obj, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                etiquetas_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon {categorias_creadas} categorías nuevas.'))
        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon {etiquetas_creadas} etiquetas nuevas.'))
        self.stdout.write(self.style.SUCCESS('El catálogo está listo para usarse.'))