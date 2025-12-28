import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0004_actionuser_sectionuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="FilterUser",
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
        migrations.AddField(
            model_name="user",
            name="numeric_range",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Numeric Range"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="numeric_range_custom",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Numeric Range Custom"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="numeric_single",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Numeric Single"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="numeric_slider",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Numeric Slider"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="numeric_slider_custom",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Numeric Slider Custom"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="numeric_wrong_type",
            field=models.CharField(
                blank=True, null=True, verbose_name="Numeric Wrong Type"
            ),
        ),
    ]
