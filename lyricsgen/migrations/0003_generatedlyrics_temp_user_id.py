# Generated by Django 5.2 on 2025-05-02 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lyricsgen", "0002_generatedlyrics_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="generatedlyrics",
            name="temp_user_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
