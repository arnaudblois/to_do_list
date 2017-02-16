from test_plus.test import TestCase
from ..forms import ProfileForm, UserUpdateForm, UserProfileForm
from to_do_list.tasks.tests.factories import TaskFactory, ProfileFactory, TeamFactory
from to_do_list.users.tests.factories import UserFactory


class TestProfileForm(TestCase):

    def setUp(self):
        UserFactory.reset_sequence()
        self.user = UserFactory()
        self.team = TeamFactory()
        self.valid_data = {
            'has_signed': 'on',
            'team': self.team.pk
        }

    def test_all_valid(self):
        """ self.valid_data should yield a valid form """
        form = ProfileForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_no_team(self):
        """
        No team selected -- form.errors should contain a single error called 'team'
        """
        data = self.valid_data
        data.pop('team')
        form = ProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('team' in form.errors)

    def test_invalid_team(self):
        """
        Team requested doesn't exist -- form.errors should contain a single error called 'team'
        """
        data = self.valid_data
        data['team'] = 42
        form = ProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('team' in form.errors)

    def test_not_signed(self):
        """
        users hasn't accepted Terms and Conditions
        """
        data = self.valid_data
        data.pop('has_signed')
        form = ProfileForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('has_signed' in form.errors)


class TestUserUpdateForm(TestCase):
    
    def setUp(self):
        self.user = self.make_user()
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_valid(self):
        """ tests valid form """
        form = UserUpdateForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_no_first_name(self):
        """ No first name -- form.errors should contain a single error called 'first_name' """
        data = self.valid_data
        data.pop('first_name')
        form = UserUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('first_name' in form.errors)

    def test_no_last_name(self):
        """ No last name -- form.errors should contain a single error called 'first_name' """
        data = self.valid_data
        data.pop('last_name')
        form = UserUpdateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('last_name' in form.errors)


class TestUserProfileForm(TestCase):
    """ Test Case for the Form combining UserUpdateForm and TestProfileForm"""
    def setUp(self):
        UserFactory.reset_sequence()
        self.user = UserFactory()
        self.team = TeamFactory()
        self.valid_data = {
            'team': self.team.pk,
            'has_signed': 'on',
            'first_name': 'John',
            'last_name': 'Doe',
        }

    def test_validity(self):
        form = UserProfileForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())
