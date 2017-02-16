import factory
from ...users.tests.factories import UserFactory


class TeamFactory(factory.django.DjangoModelFactory):
    """ Factory creating team 'Test Team' """
    name = "Test Team"
    class Meta:
        model = 'tasks.Team'


class ProfileFactory(factory.django.DjangoModelFactory):
    """ Factory creating a new profile """
    user = factory.SubFactory(UserFactory)
    has_signed = True
    team = factory.SubFactory(TeamFactory)

    class Meta:
        model = 'tasks.Profile'


class TaskFactory(factory.django.DjangoModelFactory):
    """ Factory creating a new private task """
    creator = factory.SubFactory(UserFactory)
    name = "Perform a test"
    description = "This is a test description"
    visibility = 0
    difficulty = 2

    class Meta:
        model = 'tasks.Task'
