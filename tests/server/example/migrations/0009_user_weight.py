from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0008_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="weight",
            field=models.PositiveIntegerField(
                db_index=True, default=0, verbose_name="weight"
            ),
        ),
    ]
