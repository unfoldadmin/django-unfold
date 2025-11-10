from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0004_actionuser_sectionuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                (
                    "title",
                    models.CharField(max_length=200, verbose_name="Title"),
                ),
                (
                    "content",
                    models.TextField(
                        help_text="Write your article in Markdown format",
                        verbose_name="Content",
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True,
                        help_text="Short summary in Markdown",
                        null=True,
                        verbose_name="Summary",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
            ],
            options={
                "verbose_name": "Article",
                "verbose_name_plural": "Articles",
                "ordering": ["-created_at"],
            },
        ),
    ]

