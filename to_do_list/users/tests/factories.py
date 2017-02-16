import factory


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = 'John'
    last_name = 'Doe'

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username', )
