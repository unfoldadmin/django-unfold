import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0003_tag_user_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActionUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("example.user",),
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="SectionUser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("example.user",),
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
