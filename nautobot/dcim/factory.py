import factory
from factory.django import DjangoModelFactory

from nautobot.dcim.models import Location, LocationType, Region, Site
from nautobot.tenancy.models import Tenant
from nautobot.utilities.factory import random_instance


class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region
        exclude = (
            "has_parent",
            "has_description",
        )

    name = factory.Sequence(lambda n: f"region-{n:02d}")

    has_parent = factory.Faker("pybool")
    parent = factory.Maybe("has_description", random_instance(Region), None)

    has_description = factory.Faker("pybool")
    description = factory.Maybe("has_description", factory.Faker("text", max_nb_chars=200), "")


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = Site

    name = factory.Sequence(lambda n: f"site-{n:02d}")
    region = random_instance(Region)


class LocationTypeFactory(DjangoModelFactory):
    class Meta:
        model = LocationType
        exclude = ("has_description",)

    name = factory.Sequence(lambda n: "Root" if n == 0 else ("Building" if n == 1 else ("Floor" if n == 2 else "Room")))
    parent = factory.Sequence(
        lambda n: None
        if (n == 0 or n == 1)
        else (LocationType.objects.get(name="Building") if n == 2 else LocationType.objects.get(name="Floor"))
    )

    has_description = factory.Faker("pybool")
    description = factory.Maybe("has_description", factory.Faker("text", max_nb_chars=200), "")


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location
        exclude = (
            "has_parent",
            "has_site",
            "has_tenant",
            "has_description",
        )

    location_type = random_instance(LocationType)
    name = factory.LazyAttributeSequence(lambda l, n: f"{l.location_type.name}-{n:02d}")

    has_parent = factory.LazyAttribute(lambda l: bool(l.location_type.parent))
    parent = factory.Maybe(
        "has_parent",
        factory.LazyAttribute(
            lambda l: factory.random.randgen.choice(Location.objects.filter(location_type=l.location_type.parent))
            if Location.objects.count()
            else None
        ),
    )

    has_site = factory.LazyAttribute(lambda l: not bool(l.has_parent))
    site = factory.Maybe("has_site", random_instance(Site))

    has_tenant = factory.Faker("pybool")
    tenant = factory.Maybe("has_tenant", random_instance(Tenant))

    has_description = factory.Faker("pybool")
    description = factory.Maybe("has_description", factory.Faker("text", max_nb_chars=200), "")
