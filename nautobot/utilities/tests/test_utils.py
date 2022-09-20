from django import forms
from django.db.models import Q
from django.http import QueryDict
from django.test import TestCase

from nautobot.core.settings_funcs import is_truthy
from nautobot.utilities.forms import DatePicker, DateTimePicker, DynamicModelMultipleChoiceField
from nautobot.utilities.utils import (
    build_lookup_label,
    get_values_display_names,
    convert_querydict_to_factory_formset_acceptable_querydict,
    deepmerge,
    dict_to_filter_params,
    get_all_lookup_exper_for_field,
    get_filterable_params_from_filter_params,
    get_filterset_for_model,
    get_filterset_parameter_form_field,
    get_form_for_model,
    get_model_from_name,
    get_route_for_model,
    get_table_for_model,
    is_taggable,
    is_single_choice_field,
    normalize_querydict,
    pretty_print_query,
    slugify_dots_to_dashes,
    slugify_dashes_to_underscores,
)
from nautobot.dcim.models import Device, Region, Site
from nautobot.dcim.filters import DeviceFilterSet, SiteFilterSet
from nautobot.dcim.forms import DeviceForm, DeviceFilterForm, SiteForm, SiteFilterForm
from nautobot.dcim.tables import DeviceTable, SiteTable

from example_plugin.models import ExampleModel


class DictToFilterParamsTest(TestCase):
    """
    Validate the operation of dict_to_filter_params().
    """

    def test_dict_to_filter_params(self):

        input_ = {
            "a": True,
            "foo": {
                "bar": 123,
                "baz": 456,
            },
            "x": {"y": {"z": False}},
        }

        output = {
            "a": True,
            "foo__bar": 123,
            "foo__baz": 456,
            "x__y__z": False,
        }

        self.assertEqual(dict_to_filter_params(input_), output)

        input_["x"]["y"]["z"] = True

        self.assertNotEqual(dict_to_filter_params(input_), output)


class NormalizeQueryDictTest(TestCase):
    """
    Validate normalize_querydict() utility function.
    """

    def test_normalize_querydict(self):
        self.assertDictEqual(
            normalize_querydict(QueryDict("foo=1&bar=2&bar=3&baz=")),
            {"foo": "1", "bar": ["2", "3"], "baz": ""},
        )


class DeepMergeTest(TestCase):
    """
    Validate the behavior of the deepmerge() utility.
    """

    def test_deepmerge(self):

        dict1 = {
            "active": True,
            "foo": 123,
            "fruits": {
                "orange": 1,
                "apple": 2,
                "pear": 3,
            },
            "vegetables": None,
            "dairy": {
                "milk": 1,
                "cheese": 2,
            },
            "deepnesting": {
                "foo": {
                    "a": 10,
                    "b": 20,
                    "c": 30,
                },
            },
        }

        dict2 = {
            "active": False,
            "bar": 456,
            "fruits": {
                "banana": 4,
                "grape": 5,
            },
            "vegetables": {
                "celery": 1,
                "carrots": 2,
                "corn": 3,
            },
            "dairy": None,
            "deepnesting": {
                "foo": {
                    "a": 100,
                    "d": 40,
                },
            },
        }

        merged = {
            "active": False,
            "foo": 123,
            "bar": 456,
            "fruits": {
                "orange": 1,
                "apple": 2,
                "pear": 3,
                "banana": 4,
                "grape": 5,
            },
            "vegetables": {
                "celery": 1,
                "carrots": 2,
                "corn": 3,
            },
            "dairy": None,
            "deepnesting": {
                "foo": {
                    "a": 100,
                    "b": 20,
                    "c": 30,
                    "d": 40,
                },
            },
        }

        self.assertEqual(deepmerge(dict1, dict2), merged)


class GetFooForModelTest(TestCase):
    """Tests for the various `get_foo_for_model()` functions."""

    def test_get_filterset_for_model(self):
        """
        Test the util function `get_filterset_for_model` returns the appropriate FilterSet, if model (as dotted string or class) provided.
        """
        self.assertEqual(get_filterset_for_model("dcim.device"), DeviceFilterSet)
        self.assertEqual(get_filterset_for_model(Device), DeviceFilterSet)
        self.assertEqual(get_filterset_for_model("dcim.site"), SiteFilterSet)
        self.assertEqual(get_filterset_for_model(Site), SiteFilterSet)

    def test_get_form_for_model(self):
        """
        Test the util function `get_form_for_model` returns the appropriate Form, if form type and model (as dotted string or class) provided.
        """
        self.assertEqual(get_form_for_model("dcim.device", "Filter"), DeviceFilterForm)
        self.assertEqual(get_form_for_model(Device, "Filter"), DeviceFilterForm)
        self.assertEqual(get_form_for_model("dcim.site", "Filter"), SiteFilterForm)
        self.assertEqual(get_form_for_model(Site, "Filter"), SiteFilterForm)
        self.assertEqual(get_form_for_model("dcim.device"), DeviceForm)
        self.assertEqual(get_form_for_model(Device), DeviceForm)
        self.assertEqual(get_form_for_model("dcim.site"), SiteForm)
        self.assertEqual(get_form_for_model(Site), SiteForm)

    def test_get_route_for_model(self):
        """
        Test the util function `get_route_for_model` returns the appropriate URL route name, if model (as dotted string or class) provided.
        """
        # UI
        self.assertEqual(get_route_for_model("dcim.device", "list"), "dcim:device_list")
        self.assertEqual(get_route_for_model(Device, "list"), "dcim:device_list")
        self.assertEqual(get_route_for_model("dcim.site", "list"), "dcim:site_list")
        self.assertEqual(get_route_for_model(Site, "list"), "dcim:site_list")
        self.assertEqual(
            get_route_for_model("example_plugin.examplemodel", "list"), "plugins:example_plugin:examplemodel_list"
        )
        self.assertEqual(get_route_for_model(ExampleModel, "list"), "plugins:example_plugin:examplemodel_list")

        # API
        self.assertEqual(get_route_for_model("dcim.device", "list", api=True), "dcim-api:device-list")
        self.assertEqual(get_route_for_model(Device, "list", api=True), "dcim-api:device-list")
        self.assertEqual(get_route_for_model("dcim.site", "detail", api=True), "dcim-api:site-detail")
        self.assertEqual(get_route_for_model(Site, "detail", api=True), "dcim-api:site-detail")
        self.assertEqual(
            get_route_for_model("example_plugin.examplemodel", "list", api=True),
            "plugins-api:example_plugin-api:examplemodel-list",
        )
        self.assertEqual(
            get_route_for_model(ExampleModel, "list", api=True), "plugins-api:example_plugin-api:examplemodel-list"
        )

    def test_get_table_for_model(self):
        """
        Test the util function `get_table_for_model` returns the appropriate Table, if model (as dotted string or class) provided.
        """
        self.assertEqual(get_table_for_model("dcim.device"), DeviceTable)
        self.assertEqual(get_table_for_model(Device), DeviceTable)
        self.assertEqual(get_table_for_model("dcim.site"), SiteTable)
        self.assertEqual(get_table_for_model(Site), SiteTable)

    def test_get_model_from_name(self):
        """
        Test the util function `get_model_from_name` returns the appropriate Model, if the dotted name provided.
        """
        self.assertEqual(get_model_from_name("dcim.device"), Device)
        self.assertEqual(get_model_from_name("dcim.site"), Site)


class IsTaggableTest(TestCase):
    def test_is_taggable_true(self):
        # Classes
        self.assertTrue(is_taggable(Site))
        self.assertTrue(is_taggable(Device))

        # Instances
        self.assertTrue(is_taggable(Site(name="Test Site")))

    def test_is_taggable_false(self):
        class FakeOut:
            tags = "Nope!"

        # Classes
        self.assertFalse(is_taggable(Region))
        self.assertFalse(is_taggable(FakeOut))

        # Instances
        self.assertFalse(is_taggable(Region(name="Test Region")))
        self.assertFalse(is_taggable(FakeOut()))

        self.assertFalse(is_taggable(None))


class IsTruthyTest(TestCase):
    def test_is_truthy(self):
        self.assertTrue(is_truthy("true"))
        self.assertTrue(is_truthy("True"))
        self.assertTrue(is_truthy(True))
        self.assertTrue(is_truthy("yes"))
        self.assertTrue(is_truthy("on"))
        self.assertTrue(is_truthy("y"))
        self.assertTrue(is_truthy("1"))
        self.assertTrue(is_truthy(1))

        self.assertFalse(is_truthy("false"))
        self.assertFalse(is_truthy("False"))
        self.assertFalse(is_truthy(False))
        self.assertFalse(is_truthy("no"))
        self.assertFalse(is_truthy("n"))
        self.assertFalse(is_truthy(0))
        self.assertFalse(is_truthy("0"))


class PrettyPrintQueryTest(TestCase):
    """Tests for `pretty_print_query()."""

    def test_pretty_print_query(self):
        """Test that each Q object, from deeply nested to flat, pretty prints as expected."""
        queries = [
            ((Q(site__slug="ams01") | Q(site__slug="ang01")) & ~Q(status__slug="active")) | Q(status__slug="planned"),
            (Q(site__slug="ams01") | Q(site__slug="ang01")) & ~Q(status__slug="active"),
            Q(site__slug="ams01") | Q(site__slug="ang01"),
            Q(site__slug="ang01") & ~Q(status__slug="active"),
            Q(site__slug="ams01", status__slug="planned"),
            Q(site__slug="ang01"),
            Q(status__id=12345),
            Q(site__slug__in=["ams01", "ang01"]),
        ]
        results = [
            """\
(
  (
    (
      site__slug='ams01' OR site__slug='ang01'
    ) AND (
      NOT (status__slug='active')
    )
  ) OR status__slug='planned'
)""",
            """\
(
  (
    site__slug='ams01' OR site__slug='ang01'
  ) AND (
    NOT (status__slug='active')
  )
)""",
            """\
(
  site__slug='ams01' OR site__slug='ang01'
)""",
            """\
(
  site__slug='ang01' AND (
    NOT (status__slug='active')
  )
)""",
            """\
(
  site__slug='ams01' AND status__slug='planned'
)""",
            """\
(
  site__slug='ang01'
)""",
            """\
(
  status__id=12345
)""",
            """\
(
  site__slug__in=['ams01', 'ang01']
)""",
        ]

        tests = zip(queries, results)

        for query, expected in tests:
            with self.subTest(query=query):
                self.assertEqual(pretty_print_query(query), expected)


class SlugifyFunctionsTest(TestCase):
    """Test custom slugify functions."""

    def test_slugify_dots_to_dashes(self):
        for content, expected in (
            ("Hello.World", "hello-world"),
            ("plugins.my_plugin.jobs", "plugins-my_plugin-jobs"),
            ("Lots of . spaces  ... and such", "lots-of-spaces-and-such"),
        ):
            self.assertEqual(slugify_dots_to_dashes(content), expected)

    def test_slugify_dashes_to_underscores(self):
        for content, expected in (
            ("Sites / Regions", "sites_regions"),
            ("alpha-beta_gamma delta", "alpha_beta_gamma_delta"),
        ):
            self.assertEqual(slugify_dashes_to_underscores(content), expected)


class LookupRelatedFunctionTest(TestCase):
    def test_is_single_choice_field(self):
        # Assert function returns True for any field starting with create or has_
        # Cause these fields are either boolean fields or date time fields which one accepts single values
        filterset_class = SiteFilterSet

        single_choice_fields = ("created", "created__gte", "has_vlans", "has_clusters")
        for field in single_choice_fields:
            self.assertTrue(is_single_choice_field(filterset_class, field))

        multi_choice_fields = ("status", "tenant", "tag")
        for field in multi_choice_fields:
            self.assertFalse(is_single_choice_field(filterset_class, field))

    def test_build_lookup_label(self):
        with self.subTest():
            label = build_lookup_label("slug__iew", "iendswith")
            self.assertEqual(label, "ends-with(iew)")

        with self.subTest("Test negation"):
            label = build_lookup_label("slug__niew", "iendswith")
            self.assertEqual(label, "not-ends-with(niew)")

        with self.subTest("Test for exact: without a lookup expr"):
            label = build_lookup_label("slug", "exact")
            self.assertEqual(label, "exact")

    def test_get_all_lookup_exper_for_field(self):
        with self.subTest():
            lookup_expr = get_all_lookup_exper_for_field(Site, "status")
            self.assertEqual(
                lookup_expr,
                [{"id": "status", "name": "exact"}, {"id": "status__n", "name": "not-exact(n)"}],
            )

        with self.subTest("Test field with has_ prefix"):
            lookup_expr = get_all_lookup_exper_for_field(Site, "has_vlans")
            self.assertEqual(
                lookup_expr,
                [{"id": "has_vlans", "name": "exact"}],
            )

        with self.subTest("Test unknown field"):
            lookup_expr = get_all_lookup_exper_for_field(Site, "unknown_field")
            self.assertEqual(lookup_expr, [])

    def test_get_filterset_parameter_form_field(self):
        with self.subTest("Test get CharFields"):
            site_fields = ["comments", "name", "contact_email", "physical_address", "shipping_address"]
            for field_name in site_fields:
                form_field = get_filterset_parameter_form_field(Site, field_name)
                self.assertTrue(isinstance(form_field, forms.CharField))

            device_fields = ["comments", "name"]
            for field_name in device_fields:
                form_field = get_filterset_parameter_form_field(Device, field_name)
                self.assertTrue(isinstance(form_field, forms.CharField))

        with self.subTest("Test IntegerField"):
            form_field = get_filterset_parameter_form_field(Site, "asn")
            self.assertTrue(isinstance(form_field, forms.IntegerField))

            device_fields = ["vc_position", "vc_priority"]
            for field_name in device_fields:
                form_field = get_filterset_parameter_form_field(Device, field_name)
                self.assertTrue(isinstance(form_field, forms.IntegerField))

        with self.subTest("Test DynamicModelMultipleChoiceField"):
            site_fields = ["region", "tenant", "status"]
            for field_name in site_fields:
                form_field = get_filterset_parameter_form_field(Site, field_name)
                self.assertTrue(isinstance(form_field, DynamicModelMultipleChoiceField))

            device_fields = ["cluster_id", "device_type_id", "region"]
            for field_name in device_fields:
                form_field = get_filterset_parameter_form_field(Device, field_name)
                self.assertTrue(isinstance(form_field, DynamicModelMultipleChoiceField))

        with self.subTest("Test ChoiceField"):
            site_fields = ["has_locations", "has_circuit_terminations", "has_devices"]
            for field_name in site_fields:
                form_field = get_filterset_parameter_form_field(Site, field_name)
                self.assertTrue(isinstance(form_field, forms.ChoiceField))

            device_fields = ["has_console_ports", "has_interfaces", "face"]
            for field_name in device_fields:
                form_field = get_filterset_parameter_form_field(Device, field_name)
                self.assertTrue(isinstance(form_field, forms.ChoiceField))

        with self.subTest("Test DateTimePicker"):
            form_field = get_filterset_parameter_form_field(Site, "last_updated")
            self.assertTrue(isinstance(form_field.widget, DateTimePicker))

            form_field = get_filterset_parameter_form_field(Device, "last_updated")
            self.assertTrue(isinstance(form_field.widget, DateTimePicker))

        with self.subTest("Test DatePicker"):
            form_field = get_filterset_parameter_form_field(Site, "created")
            self.assertTrue(isinstance(form_field.widget, DatePicker))

            form_field = get_filterset_parameter_form_field(Device, "created")
            self.assertTrue(isinstance(form_field.widget, DatePicker))

    def test_compile_model_instance_choices(self):
        sites = (
            Site.objects.create(name="Site 1", slug="site-1"),
            Site.objects.create(name="Site 2", slug="site-2"),
        )

        with self.subTest("Get choices of valid fields"):
            choices = get_values_display_names(Site, "slug", ["site-1", "site-2"])
            self.assertEqual(
                choices,
                [
                    (sites[0].slug, sites[0].name),
                    (sites[1].slug, sites[1].name),
                ],
            )

        with self.subTest("Get choices for invalid fields"):
            choices = get_values_display_names(Site, "slug", ["site-3", "site-4"])
            self.assertEqual(choices, [])

    def test_convert_querydict_to_factory_formset_dict(self):
        with self.subTest("Convert QueryDict to an acceptable factory formset QueryDict and discards invalid params"):
            request_querydict = QueryDict(mutable=True)
            request_querydict.setlistdefault("status", ["active", "decommissioning"])
            request_querydict.setlistdefault("name__ic", ["site"])
            request_querydict.setlistdefault("invalid_field", ["invalid"])  # Should be ignored
            request_querydict.setlistdefault("name__iew", [""])  # Should be ignored since it has no value

            data = convert_querydict_to_factory_formset_acceptable_querydict(request_querydict, SiteFilterSet)
            expected_querydict = QueryDict(mutable=True)
            expected_querydict.setlistdefault("form-TOTAL_FORMS", [3])
            expected_querydict.setlistdefault("form-INITIAL_FORMS", [0])
            expected_querydict.setlistdefault("form-MIN_NUM_FORMS", [0])
            expected_querydict.setlistdefault("form-MAX_NUM_FORMS", [100])
            expected_querydict.setlistdefault("form-0-lookup_field", ["status"])
            expected_querydict.setlistdefault("form-0-lookup_type", ["status"])
            expected_querydict.setlistdefault("form-0-lookup_value", ["active", "decommissioning"])
            expected_querydict.setlistdefault("form-1-lookup_field", ["name"])
            expected_querydict.setlistdefault("form-1-lookup_type", ["name__ic"])
            expected_querydict.setlistdefault("form-1-lookup_value", ["site"])

            self.assertEqual(data, expected_querydict)

        with self.subTest("Convert an empty QueryDict to an acceptable factory formset QueryDict"):
            request_querydict = QueryDict(mutable=True)

            data = convert_querydict_to_factory_formset_acceptable_querydict(request_querydict, SiteFilterSet)
            expected_querydict = QueryDict(mutable=True)
            expected_querydict.setlistdefault("form-TOTAL_FORMS", [3])
            expected_querydict.setlistdefault("form-INITIAL_FORMS", [0])
            expected_querydict.setlistdefault("form-MIN_NUM_FORMS", [0])
            expected_querydict.setlistdefault("form-MAX_NUM_FORMS", [100])

            self.assertEqual(data, expected_querydict)

    def test_get_filterable_params_from_filter_params(self):
        filter_params = QueryDict(mutable=True)
        filter_params.update({"page": "1", "per_page": "20", "name": "Site 1"})
        filter_params.setlistdefault("status", ["active", "planned"])

        non_filter_params = ["page", "per_page"]
        filterset_class = SiteFilterSet
        data = get_filterable_params_from_filter_params(filter_params, non_filter_params, filterset_class)

        self.assertEqual(data, {"name": ["Site 1"], "status": ["active", "planned"]})
