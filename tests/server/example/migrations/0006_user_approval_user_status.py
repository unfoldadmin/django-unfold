from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example", "0005_filteruser_user_numeric_range_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="approval",
            field=models.CharField(
                blank=True,
                choices=[
                    ("new", "New"),
                    ("reviewed", "Reviewed"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="new",
                max_length=20,
                null=True,
                verbose_name="Approval",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("active", "Active"),
                    ("inactive", "Inactive"),
                    ("pending", "Pending"),
                ],
                default="active",
                max_length=20,
                null=True,
                verbose_name="Status",
            ),
        ),
    ]
