# Generated by Django 3.2.15 on 2022-09-05 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0049_customfield_grouping"),
    ]

    operations = [
        migrations.AddField(
            model_name="relationship",
            name="required",
            field=models.CharField(blank=True, default="", max_length=12),
        ),
    ]
