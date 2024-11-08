# Generated by Django 4.2.11 on 2024-03-16 22:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Story",
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
                ("headline", models.CharField(max_length=64)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("pol", "Politics"),
                            ("art", "Art"),
                            ("tech", "Technology"),
                            ("trivia", "Trivia"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("uk", "UK"),
                            ("eu", "European Union"),
                            ("w", "World"),
                        ],
                        max_length=2,
                    ),
                ),
                ("date", models.DateField()),
                ("details", models.CharField(max_length=128)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
            },
        ),
    ]
