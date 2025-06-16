from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0002_user_content_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
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
        migrations.AddField(
            model_name="user",
            name="tags",
            field=models.ManyToManyField(blank=True, to="example.tag"),
        ),
    ]
