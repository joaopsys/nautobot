from django.db.models import Model

import factory
import factory.random


def _get_queryset_from_model_or_queryset_or_lambda(model_or_queryset_or_lambda):
    if isinstance(model_or_queryset_or_lambda, type) and issubclass(model_or_queryset_or_lambda, Model):
        queryset = model_or_queryset_or_lambda.objects.all()
    elif callable(model_or_queryset_or_lambda):
        model_or_queryset = model_or_queryset_or_lambda()
        if isinstance(model_or_queryset, type) and issubclass(model_or_queryset, Model):
            queryset = model_or_queryset.objects.all()
        else:
            queryset = model_or_queryset
    else:
        queryset = model_or_queryset_or_lambda

    return queryset


def random_instance(model_or_queryset_or_lambda, allow_null=True):
    """
    Factory helper - construct a LazyFunction that gets a random instance of the given model or queryset when evaluated.

    TODO: once we have factories for all mandatory foreign keys, change allow_null default to False

    Args:
        model_or_queryset_or_lambda: Either a model class, a model queryset, or a lambda that returns one of those
        allow_null (bool): If False, and the given queryset contains no objects, raise a RuntimeError.

    Example:
        class ObjectFactory(DjangoModelFactory):
            class Meta:
                model = Object
                exclude = ("has_group,")

            # Required foreign key
            user = random_instance(User, allow_null=False)

            # Optional foreign key
            has_group = factory.Faker("pybool")
            group = factory.Maybe("has_group", random_instance(Group), None)

            # Foreign key selected from a filtered queryset
            tenant = random_instance(Tenant.objects.filter(group__isnull=False))

            # Foreign key selected from a queryset generated by a lambda
            # This needs to be done this way because .get_for_model() evaluates a ContentType queryset,
            # and we need to defer evaluation of that queryset as well.
            status = random_instance(lambda: Status.objects.get_for_model(Object), allow_null=False)
    """

    def get_random_instance():
        queryset = _get_queryset_from_model_or_queryset_or_lambda(model_or_queryset_or_lambda)

        if not allow_null and not queryset.exists():
            raise RuntimeError(f"No objects in queryset for {model_or_queryset_or_lambda}! {queryset.explain()}")

        return factory.random.randgen.choice(queryset) if queryset.exists() else None

    return factory.LazyFunction(get_random_instance)


def get_random_instances(model_or_queryset_or_lambda, maximum=None):
    """
    Factory helper - retrieve a random number of instances of the given model.

    This is different from random_instance() in that it's not itself a lazy function generator, but should instead be
    called only from within a @lazy_attribute or @post_generation function.

    This is not an evenly weighted distribution (all counts equally likely), because in most of our code,
    the relevant code paths distinguish between 0, 1, or >1 instances - there's not a functional difference between
    "2 instances" and "10 instances" in most cases. Therefore, this implementation provides:
        - 1/3 chance of no instances
        - 1/3 chance of 1 instance
        - 1/3 chance of (2 to n) instances, where each possibility is equally likely within this range

    Args:
        model_or_queryset_or_lambda: Either a model class, a model queryset, or a lambda that returns one of those
        maximum (int): Maximum number of objects to return, or None for no limit
    """
    branch = factory.random.randgen.randint(0, 2)
    queryset = _get_queryset_from_model_or_queryset_or_lambda(model_or_queryset_or_lambda)
    count = queryset.count()
    if maximum is None:
        maximum = count
    if branch == 0 or count == 0 or maximum == 0:
        return []
    if branch == 1 or count == 1 or maximum == 1:
        return [factory.random.randgen.choice(queryset)]
    return factory.random.randgen.sample(
        population=list(queryset),
        k=factory.random.randgen.randint(2, min(maximum, count)),
    )


class UniqueFaker(factory.Faker):
    """https://github.com/FactoryBoy/factory_boy/pull/820#issuecomment-1004802669"""

    @classmethod
    def _get_faker(cls, locale=None):
        return super()._get_faker(locale=locale).unique
