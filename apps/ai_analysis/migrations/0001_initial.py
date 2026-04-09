from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("properties", "0003_reviews"),
    ]

    operations = [
        migrations.CreateModel(
            name="PhotoSubjectiveAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attribute_token", models.CharField(max_length=100)),
                ("strength", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("photo", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="subjective_attributes", to="properties.propertiesphotos")),
                ("property", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="photo_subjective_attributes", to="properties.properties")),
            ],
            options={
                "ordering": ["attribute_token"],
                "unique_together": {("photo", "attribute_token")},
            },
        ),
        migrations.CreateModel(
            name="PropertySubjectiveAttribute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attribute_token", models.CharField(max_length=100)),
                ("strength_mean", models.FloatField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("property", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="subjective_attributes", to="properties.properties")),
            ],
            options={
                "ordering": ["attribute_token"],
                "unique_together": {("property", "attribute_token")},
            },
        ),
    ]
