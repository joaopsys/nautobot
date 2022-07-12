# Generated by Django 3.2.13 on 2022-06-15 14:00

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.fields
import nautobot.extras.models.mixins
import nautobot.extras.models.statuses
import nautobot.extras.utils
import nautobot.utilities.fields
import nautobot.utilities.ordering
import taggit.managers
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("tenancy", "0001_initial"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0035_configcontextschema__remove_name_unique__create_constraint_unique_name_owner"),
        ("dcim", "0012_interface_parent_bridge"),
    ]

    operations = [
        migrations.CreateModel(
            name="LocationType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "slug",
                    nautobot.core.fields.AutoSlugField(blank=True, max_length=100, populate_from="name", unique=True),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "content_types",
                    models.ManyToManyField(
                        limit_choices_to=nautobot.extras.utils.FeatureQuery("locations"),
                        related_name="location_types",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="dcim.locationtype",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin),
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(db_index=True, max_length=100)),
                (
                    "_name",
                    nautobot.utilities.fields.NaturalOrderingField(
                        "name",
                        blank=True,
                        db_index=True,
                        max_length=100,
                        naturalize_function=nautobot.utilities.ordering.naturalize,
                    ),
                ),
                (
                    "slug",
                    nautobot.core.fields.AutoSlugField(
                        blank=True, max_length=100, populate_from=["parent__slug", "name"], unique=True
                    ),
                ),
                ("description", models.CharField(blank=True, max_length=200)),
                (
                    "location_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="locations", to="dcim.locationtype"
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="dcim.location",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="locations",
                        to="dcim.site",
                    ),
                ),
                (
                    "status",
                    nautobot.extras.models.statuses.StatusField(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="dcim_location_related",
                        to="extras.status",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="locations",
                        to="tenancy.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("_name",),
            },
            bases=(models.Model, nautobot.extras.models.mixins.DynamicGroupMixin),
        ),
        migrations.AddField(
            model_name="device",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="devices",
                to="dcim.location",
            ),
        ),
        migrations.AddField(
            model_name="powerpanel",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="powerpanels",
                to="dcim.location",
            ),
        ),
        migrations.AddField(
            model_name="rack",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="racks",
                to="dcim.location",
            ),
        ),
        migrations.AddField(
            model_name="rackgroup",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rack_groups",
                to="dcim.location",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="location",
            unique_together={("parent", "name")},
        ),
    ]