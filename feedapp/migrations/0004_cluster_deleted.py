# Generated by Django 4.0.4 on 2022-04-24 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedapp", "0003_cluster"),
    ]

    operations = [
        migrations.AddField(
            model_name="cluster",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]
