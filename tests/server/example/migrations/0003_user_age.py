# Generated by Django 4.2.18 on 2025-03-06 05:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0002_user_content_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="age",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
