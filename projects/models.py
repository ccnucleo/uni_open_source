from django.conf import settings
from django.db import models


class Project(models.Model):
	title = models.CharField(max_length=120)
	summary = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	tech_stack = models.CharField(max_length=120, blank=True)
	repository_url = models.URLField(blank=True)
	demo_url = models.URLField(blank=True)
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="owned_projects",
	)
	is_public = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title
