from test_plus.test import TestCase
from ..models import Profile, Task, Team
from .factories import ProfileFactory, TaskFactory, TeamFactory
from to_do_list.users.tests.factories import UserFactory


class TestProfile(TestCase):

    def setUp(self):
        UserFactory.reset_sequence()
        self.user = UserFactory()
        self.profile = ProfileFactory(user=self.user)

    def test__str__(self):
        self.assertEqual(
            self.profile.__str__(),
            "user-0's profile"
        )


class TestTask(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.profile = ProfileFactory(user=self.user)
        self.task = TaskFactory(creator=self.user)

    def test__str__(self):
        self.assertEqual(
            self.task.__str__(),
            'Perform a test'
        )

    def test_is_new(self):
        self.assertTrue(self.task.is_new())
        self.task.status = Task.STATUS.completed
        self.task.save()
        self.assertFalse(self.task.is_new())

    def test_is_visible_by(self):
        # profile2 is in the same team as self.profile
        # profile3 has nothing in common
        profile2 = ProfileFactory(team=self.profile.team)
        other_team = TeamFactory(name='the Others')
        profile3 = ProfileFactory(team=other_team)
        # self.task is private, only visible to self.user
        self.assertTrue(self.task.is_visible_by(self.user))
        self.assertFalse(self.task.is_visible_by(profile2.user))
        self.assertFalse(self.task.is_visible_by(profile3.user))
        # task2 set to team_only, visible to profile2 as well
        task2 = TaskFactory(creator=self.user, visibility=Task.VISIBILITIES.team_only)
        self.assertTrue(task2.is_visible_by(self.user))
        self.assertTrue(task2.is_visible_by(profile2.user))
        self.assertFalse(task2.is_visible_by(profile3.user))
        # task2 set to team_only, visible to profile2 as well
        task3 = TaskFactory(creator=self.user, visibility=Task.VISIBILITIES.public)
        self.assertTrue(task3.is_visible_by(self.user))
        self.assertTrue(task3.is_visible_by(profile2.user))
        self.assertTrue(task3.is_visible_by(profile3.user))


class TestTeam(TestCase):
    def setUp(self):
        UserFactory.reset_sequence()
        self.team = TeamFactory()

    def test__str__(self):
        self.assertEqual(
            self.team.__str__(),
            'Test Team'
        )
