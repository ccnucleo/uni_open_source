from django.conf import settings
from django.db import models


class Course(models.Model):
	BEGINNER = "beginner"
	INTERMEDIATE = "intermediate"
	ADVANCED = "advanced"
	LEVEL_CHOICES = [
		(BEGINNER, "Beginner"),
		(INTERMEDIATE, "Intermediate"),
		(ADVANCED, "Advanced"),
	]

	title = models.CharField(max_length=120)
	short_description = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	category = models.CharField(max_length=80, blank=True)
	level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=BEGINNER)
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="owned_courses",
	)
	is_published = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title
