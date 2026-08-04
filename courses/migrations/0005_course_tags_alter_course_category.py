import django.db.models.deletion
from django.db import migrations, models


def populate_categories(apps, schema_editor):
    Category = apps.get_model("courses", "Category")
    Course = apps.get_model("courses", "Course")
    for course in Course.objects.all():
        if course.category:
            category, _ = Category.objects.get_or_create(name=course.category)
            course.category = str(category.id)
            course.save()


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0004_category_tag_alter_course_category"),
    ]
    operations = [
        migrations.AddField(
            model_name="course",
            name="tags",
            field=models.ManyToManyField(
                blank=True, to="courses.tag", verbose_name="Tecnologías"
            ),
        ),
        migrations.RunPython(populate_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="course",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="courses.category",
                verbose_name="Categoría Temática",
            ),
        ),
    ]