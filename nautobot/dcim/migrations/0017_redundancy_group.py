# Generated by Django 3.2.15 on 2022-10-13 18:40

import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import nautobot.extras.models.mixins
import nautobot.extras.models.models
import nautobot.extras.models.statuses
import nautobot.extras.utils
import taggit.managers
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0050_add_job_task_queues"),
        ("dcim", "0016_device_components__timestamp_data_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="redundancy_group_priority",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.CreateModel(
            name="RedundancyGroup",
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
                (
                    "local_context_data",
                    models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
                ),
                ("local_context_data_owner_object_id", models.UUIDField(blank=True, default=None, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("failover_strategy", models.CharField(blank=True, max_length=50)),
                ("comments", models.TextField(blank=True)),
                (
                    "local_context_data_owner_content_type",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        limit_choices_to=nautobot.extras.utils.FeatureQuery("config_context_owners"),
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "local_context_schema",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="extras.configcontextschema",
                    ),
                ),
                (
                    "secrets_group",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="extras.secretsgroup",
                    ),
                ),
                (
                    "status",
                    nautobot.extras.models.statuses.StatusField(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="dcim_redundancygroup_related",
                        to="extras.status",
                    ),
                ),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(
                models.Model,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                nautobot.extras.models.models.ConfigContextSchemaValidationMixin,
            ),
        ),
        migrations.AddField(
            model_name="device",
            name="redundancy_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="members",
                to="dcim.redundancygroup",
            ),
        ),
    ]