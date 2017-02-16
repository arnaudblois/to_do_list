from test_plus.test import TestCase
from ..models import Profile, Task, Team
from .factories import ProfileFactory, TaskFactory, TeamFactory
from to_do_list.users.tests.factories import UserFactory

from ..helper_functions import calculate_reputation_gain, give_reputation_reward
from mock import patch


class TestProfile(TestCase):

    def setUp(self):
        UserFactory.reset_sequence()
        team = TeamFactory()
        self.user1 = UserFactory()
        profile = ProfileFactory(user=self.user1, team=team)
        self.user2 = UserFactory()
        self.profile2 = ProfileFactory(user=self.user2, team=team)

    def test_trivial_task(self):
        """ solving trivial task is worth 1 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.trivial,
        )
        self.assertEqual(calculate_reputation_gain(task), 1)

    def test_easy_task(self):
        """ solving easy task is worth 5 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.easy,
        )
        self.assertEqual(calculate_reputation_gain(task), 5)

    def test_OK_task(self):
        """ solving OK task is worth 10 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.OK,
        )
        self.assertEqual(calculate_reputation_gain(task), 10)

    def test_hard_task(self):
        """ solving hard task is worth 25 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.hard,
        )
        self.assertEqual(calculate_reputation_gain(task), 25)

    def test_heroic_task(self):
        """ solving heroic task is worth 100 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.heroic,
        )
        self.assertEqual(calculate_reputation_gain(task), 100)

    def test_nightmare_task(self):
        """ and solving nightmare task is worth 500 """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2, difficulty=Task.DIFFICULTIES.nightmare,
        )
        self.assertEqual(calculate_reputation_gain(task), 500)


    @patch('to_do_list.tasks.helper_functions.calculate_reputation_gain', lambda x: 42)
    def test_give_reputation(self):
        """
        should increase the reputation of the user who completed the task by the
        gain calculated (here patched to always return 42)
        """
        task = TaskFactory(
            creator=self.user1, visibility=Task.VISIBILITIES.public,
            completed_by=self.user2,
        )
        give_reputation_reward(task)
        self.profile2.refresh_from_db()
        self.assertEqual(self.profile2.reputation, 1 + 42)
