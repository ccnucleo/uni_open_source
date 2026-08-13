import json
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from projects.models import Project, Technology, Tag

User = get_user_model()


class ProjectsAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="Password123!"
        )
        self.project = Project.objects.create(
            title="Proyecto Inicial",
            summary="Descripción breve inicial para tests de API",
            description="Detalles de contexto del proyecto inicial",
            owner=self.user,
            is_public=True
        )
        self.tech = Technology.objects.create(name="Python")
        self.project.technologies.add(self.tech)

    def test_get_projects_list_api(self):
        self.client.force_login(self.user)
        response = self.client.get("/projects/api/projects/?title=Test")
        self.assertEqual(response.status_code, 200)

    def test_create_project_api_unauthenticated(self):
        response = self.client.post(
            "/projects/api/projects/",
            data=json.dumps({"title": "Nuevo sin auth"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_project_api_json(self):
        self.client.force_login(self.user)
        payload = {
            "title": "Nuevo Proyecto JSON",
            "summary": "Resumen desde API JSON válido",
            "description": "Descripción más larga",
            "technologies": "TensorFlow",
            "repository_url": "https://github.com/testuser/nuevo-json"
        }
        response = self.client.post(
            "/projects/api/projects/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))

    def test_get_project_detail_api(self):
        response = self.client.get(f"/projects/{self.project.id}/")
        self.assertEqual(response.status_code, 200)

    def test_update_project_api_owner(self):
        self.client.force_login(self.user)
        payload = {
            "title": "Proyecto Modificado",
            "technologies": "Django, React"
        }
        response = self.client.post(
            f"/projects/api/projects/{self.project.id}/",
            data=payload
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))

    def test_update_project_api_forbidden(self):
        self.client.force_login(self.other_user)
        payload = {"title": "Intento no autorizado"}
        response = self.client.post(
            f"/projects/api/projects/{self.project.id}/",
            data=payload
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_project_api(self):
        self.client.force_login(self.user)
        response = self.client.delete(f"/projects/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

