from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "projects",
            "0004_tag_alter_project_options_alter_projectimage_options_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="theme",
            field=models.CharField(
                choices=[
                    ("web", "Desarrollo Web"),
                    ("mobile", "Apps Móviles"),
                    ("ia", "IA / Machine Learning"),
                    ("data", "Data Science"),
                    ("iot", "IoT"),
                    ("games", "Videojuegos"),
                    ("security", "Seguridad"),
                    ("api", "APIs / Backend"),
                    ("devops", "DevOps"),
                    ("research", "Investigación"),
                ],
                default="web",
                max_length=20,
            ),
        ),
    ]