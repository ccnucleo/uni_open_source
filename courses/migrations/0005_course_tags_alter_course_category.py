import django.db.models.deletion
from django.db import migrations, models


def populate_categories(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    Category = apps.get_model("courses", "Category")
    for course in Course.objects.all():
        val = course.category
        if val is not None:
            val_str = str(val).strip()
            if val_str:
                if val_str.isdigit() and Category.objects.filter(id=int(val_str)).exists():
                    continue
                cat_obj, _ = Category.objects.get_or_create(name=val_str)
                course.category = str(cat_obj.id)
                course.save()
        else:
            course.category = None
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