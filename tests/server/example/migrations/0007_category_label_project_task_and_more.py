from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0006_user_approval_user_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Label",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name="user",
            name="numeric_wrong_type",
        ),
        migrations.AddField(
            model_name="user",
            name="color",
            field=models.CharField(
                blank=True,
                choices=[
                    ("red", "Red"),
                    ("blue", "Blue"),
                    ("green", "Green"),
                    ("yellow", "Yellow"),
                ],
                default="blue",
                max_length=20,
                null=True,
                verbose_name="Color",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="priority",
            field=models.CharField(
                blank=True,
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                default="medium",
                max_length=20,
                null=True,
                verbose_name="Priority",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="categories",
            field=models.ManyToManyField(blank=True, to="example.category"),
        ),
        migrations.AddField(
            model_name="user",
            name="labels",
            field=models.ManyToManyField(blank=True, to="example.label"),
        ),
        migrations.AddField(
            model_name="user",
            name="projects",
            field=models.ManyToManyField(blank=True, to="example.project"),
        ),
        migrations.AddField(
            model_name="user",
            name="tasks",
            field=models.ManyToManyField(blank=True, to="example.task"),
        ),
    ]
