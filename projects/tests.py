import json
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from projects.models import Project

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
            summary="Descripción breve inicial",
            paragraph_1="Detalles de contexto del proyecto inicial",
            main_tech="Python",
            theme="web",
            owner=self.user,
            is_public=True
        )

    def test_get_projects_list_api(self):
        response = self.client.get("/projects/api/projects/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertEqual(len(data.get("data")), 1)
        self.assertEqual(data["data"][0]["title"], "Proyecto Inicial")
        self.assertEqual(data["data"][0]["tech_stack"], "Python")

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
            "summary": "Resumen desde API JSON",
            "description": "Descripción más larga",
            "theme": "ia",
            "tech_stack": "TensorFlow",
            "repository_url": "https://github.com/testuser/nuevo-json"
        }
        response = self.client.post(
            "/projects/api/projects/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["data"]["title"], "Nuevo Proyecto JSON")
        self.assertEqual(data["data"]["tech_stack"], "TensorFlow")
        self.assertEqual(data["data"]["owner"], "testuser")

    def test_create_project_api_formdata(self):
        self.client.force_login(self.user)
        payload = {
            "title": "Nuevo Proyecto FormData",
            "summary": "Resumen de FormData",
            "description": "Descripción completa en FormData",
            "theme": "mobile",
            "main_tech": "Flutter"
        }
        response = self.client.post("/projects/api/projects/", data=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["data"]["title"], "Nuevo Proyecto FormData")
        self.assertEqual(data["data"]["main_tech"], "Flutter")

    def test_get_project_detail_api(self):
        response = self.client.get(f"/projects/api/projects/{self.project.id}/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["data"]["id"], self.project.id)

    def test_update_project_api_owner(self):
        self.client.force_login(self.user)
        payload = {
            "title": "Proyecto Modificado",
            "main_tech": "Django / React"
        }
        response = self.client.post(
            f"/projects/api/projects/{self.project.id}/",
            data=payload
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get("success"))
        self.assertEqual(data["data"]["title"], "Proyecto Modificado")
        self.assertEqual(data["data"]["tech_stack"], "Django / React")

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
