from django.test import RequestFactory
from test_plus.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from to_do_list.users.tests.factories import UserFactory
from .factories import ProfileFactory, TaskFactory, TeamFactory
from to_do_list.users.models import User
from mock import patch

from ..views import (
    home_view,
    ProfileCreateView,
    ProfileUpdateView,
    TaskCreateView,
    TaskUpdateView,
    delete_task,
    complete_task,
    close_task,
)

from to_do_list.tasks.models import Profile, Task
from bs4 import BeautifulSoup


class TestHomePage(TestCase):
    """ checking url '/' is working """
    def test_check_home(self):
        response = Client().get('/')
        self.assertEqual(response.status_code, 200)


class BaseTaskTestCase(TestCase):
    """
    A base TestCase from which most tests here inherit, provides a common setUp
    and tests for login required and profile exists
    """
    def setUp(self):
        """
        creates a new user 'user-0' and attach it to a client
        """
        UserFactory.reset_sequence()
        self.user = UserFactory()
        self.client = Client()
        self.client.login(username=self.user.username, password='password')

    def run_test_login_required(self):
        """
        makes sure that if a user is not logged in,
        she is redirected
        """
        response = Client().get(self.url)
        self.assertEqual(
            response.status_code, 302
        )

    def run_test_profile_required(self):
        """
        checks if a user which has not a completed profile is redirected
        to tasks:home
        """
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, reverse("tasks:home"), status_code=302, target_status_code=200
        )


class TestHome(BaseTaskTestCase):
    """ Test case for the home page of the tasks' section """
    def setUp(self):
        super().setUp()
        self.url = reverse('tasks:home')

    def test_login_required(self):
        self.run_test_login_required()

    def test_new_user_must_create_profile(self):
        """
        makes sure a logged-in user with no profile is provided a link to
        complete his account
        """
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'href="{0}"'.format(reverse("tasks:create_profile")),
            status_code=200,
        )

    def test_profile_no_task(self):
        """
        checks a valid user has a link to create a new task one
        """
        profile = ProfileFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:create_task")),
            status_code=200
        )


class TestHomeIndividualTask(BaseTaskTestCase):
    """
    tests going a bit more in depth regarding the display of tasks in the list
    """
    def setUp(self):
        super().setUp()
        self.url = reverse('tasks:home')
        team1 = TeamFactory(name='team1')
        profile1 = ProfileFactory(user=self.user, team=team1)
        team2 = TeamFactory(name="other_team")
        profile2 = ProfileFactory(team=team2)
        self.user2 = profile2.user

    def test_show_new_task_user_is_creator(self):
        """
        a new task belonging to the current user must have links for edition,
        deletion and closing the task
        """
        task = TaskFactory(creator=self.user)
        pk = task.pk
        response = self.client.get(self.url)

        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:update_task", kwargs={'pk': pk})), status_code=200,
        )
        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:delete_task", kwargs={'pk': pk}))
        )
        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:complete_task", kwargs={'pk': pk}))
        )
        # Link to see the details of task 1
        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:detail_task", kwargs={'pk': pk})),
        )

    def test_show_completed_task_user_is_creator(self):
        """
        a 'completed' task (ie marked as done by someone else) and created by
        the current user, must have a 'close' link and no other link
        """
        task = TaskFactory(creator=self.user, completed_by=self.user2, status=Task.STATUS.completed)
        response = self.client.get(self.url)
        self.assertContains(
            response, 'href="{0}"'.format(reverse("tasks:close_task", kwargs={'pk': task.pk})),
        )
        self.assertNotContains(
            response, reverse("tasks:delete_task", kwargs={'pk': task.pk}),
        )
        self.assertNotContains(
            response, reverse("tasks:update_task", kwargs={'pk': task.pk}),
        )

    def test_no_display_of_hidden_tasks(self):
        """ all tasks not visible to the user must not be displayed """
        TaskFactory(creator=self.user2)
        TaskFactory(creator=self.user2, visibility=Task.VISIBILITIES.team_only)
        response = self.client.get(self.url)
        self.assertContains(
            response, 'There are no task matching the search criteria...',
        )

    def test_closed_task(self):
        """
        all other tasks should have no links
        """
        TaskFactory(creator=self.user, status=Task.STATUS.assigned)
        TaskFactory(creator=self.user, status=Task.STATUS.closed)
        TaskFactory(creator=self.user2, visibility=Task.VISIBILITIES.public)
        response = self.client.get(self.url)
        self.assertNotContains(
            response, reverse("tasks:close_task", kwargs={'pk': 1})[:-2],
        )
        self.assertNotContains(
            response, reverse("tasks:delete_task", kwargs={'pk': 1})[:-2],
        )
        self.assertNotContains(
            response, reverse("tasks:update_task",kwargs={'pk': 1})[:-2],
        )


class TestHomeFilterOrderTask(BaseTaskTestCase):
    """
    tests checking the filtering and ordering of the tasks
    """
    def setUp(self):
        super().setUp()
        self.profile = ProfileFactory(user=self.user)
        self.url = reverse('tasks:home')

    def test_filter_visibility(self):
        """ only tasks matching the visibility filter must be shown """
        t1 = TaskFactory(name="private_task", creator=self.user, visibility=Task.VISIBILITIES.private)
        t2 = TaskFactory(name="team_only_task", creator=self.user, visibility=Task.VISIBILITIES.team_only)
        t3 = TaskFactory(name="public_task", creator=self.user, visibility=Task.VISIBILITIES.public)
        response = self.client.get(self.url, data={'visibility': t1.visibility})
        self.assertContains(response, t1.name, status_code=200)
        self.assertNotContains(response, t2.name)
        self.assertNotContains(response, t3.name)
        response = self.client.get(self.url, data={'visibility': t2.visibility})
        self.assertNotContains(response, t1.name, status_code=200)
        self.assertContains(response, t2.name)
        self.assertNotContains(response, t3.name)
        response = self.client.get(self.url, data={'visibility': t3.visibility})
        self.assertNotContains(response, t1.name, status_code=200)
        self.assertNotContains(response, t2.name)
        self.assertContains(response, t3.name)

    def test_filter_status(self):
        """ only tasks matching the status filter must be shown """
        t1 = TaskFactory(name="new_task", creator=self.user, status=Task.STATUS.new)
        t2 = TaskFactory(name="assigned_task", creator=self.user, status=Task.STATUS.assigned)
        t3 = TaskFactory(name="completed_task", creator=self.user, status=Task.STATUS.completed)
        t4 = TaskFactory(name="closed_task", creator=self.user, status=Task.STATUS.closed)
        # filter by status new
        response = self.client.get(self.url, data={'status': t1.status})
        self.assertContains(response, t1.name, status_code=200)
        self.assertNotContains(response, t2.name)
        self.assertNotContains(response, t3.name)
        self.assertNotContains(response, t4.name)
        # filter by status assigned
        response = self.client.get(self.url, data={'status': t2.status})
        self.assertNotContains(response, t1.name, status_code=200)
        self.assertContains(response, t2.name)
        self.assertNotContains(response, t3.name)
        self.assertNotContains(response, t4.name)
        # filter by status completed
        response = self.client.get(self.url, data={'status': t3.status})
        self.assertNotContains(response, t1.name, status_code=200)
        self.assertNotContains(response, t2.name)
        self.assertContains(response, t3.name)
        self.assertNotContains(response, t4.name)
        # filter by status closed
        response = self.client.get(self.url, data={'status': t4.status})
        self.assertNotContains(response, t1.name, status_code=200)
        self.assertNotContains(response, t2.name)
        self.assertNotContains(response, t3.name)
        self.assertContains(response, t4.name)

    def test_order_status(self):
        """
        should be possible to order by status in ascending and descending order
        """
        t4 = TaskFactory(name="closed", creator=self.user, status=Task.STATUS.closed)
        t2 = TaskFactory(name="assigned", creator=self.user, status=Task.STATUS.assigned)
        t3 = TaskFactory(name="completed", creator=self.user, status=Task.STATUS.completed)
        t1 = TaskFactory(name="new", creator=self.user, status=Task.STATUS.new)
        # ascending order
        response = self.client.get(self.url, data={'sort': 'status'})
        soup = BeautifulSoup(response.content, "html.parser")
        td_names = soup.find_all("td", class_="name")
        name_list = [name.a.get_text() for name in td_names]
        self.assertEqual(name_list, ['new', 'assigned', 'completed', 'closed'])
        # descending order
        response = self.client.get(self.url, data={'sort': '-status'})
        soup = BeautifulSoup(response.content, "html.parser")
        td_names = soup.find_all("td", class_="name")
        name_list = [name.a.get_text() for name in td_names]
        self.assertEqual(name_list, ['closed', 'completed', 'assigned', 'new'])

    def test_filter_name(self):
        """
        should be possible to order by name in ascending and descending order
        """
        t1 = TaskFactory(name="b", creator=self.user, status=Task.STATUS.new)
        t2 = TaskFactory(name="a", creator=self.user, status=Task.STATUS.assigned)
        t3 = TaskFactory(name="c", creator=self.user, status=Task.STATUS.completed)
        t4 = TaskFactory(name="e", creator=self.user, status=Task.STATUS.closed)
        t5 = TaskFactory(name="d", creator=self.user, status=Task.STATUS.new)
        # testing ascending order
        response = self.client.get(self.url, data={'sort': 'name'})
        soup = BeautifulSoup(response.content, "html.parser")
        td_names = soup.find_all("td", class_="name")
        name_list = [name.a.get_text() for name in td_names]
        self.assertEqual(name_list, ['a', 'b', 'c', 'd', 'e'])
        # testing descending
        response = self.client.get(self.url, data={'sort': '-name'})
        soup = BeautifulSoup(response.content, "html.parser")
        td_names = soup.find_all("td", class_="name")
        name_list = [name.a.get_text() for name in td_names]
        self.assertEqual(name_list, ['e', 'd', 'c', 'b', 'a'])


#  ------------------------------------------------
#                PROFILE RELATED VIEWS
#  ------------------------------------------------


class TestProfileCreateView(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('tasks:create_profile')

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_already_profile(self):
        """ if there is already a profile for the user -> redirect to tasks:home """
        profile = ProfileFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_success_url(self):
        """" should redirect to the home page """
        self.assertEqual(
            ProfileCreateView().get_success_url(),
            reverse('tasks:home')
        )

    def test_creation(self):
        """
        checks a new profile has been created upon submission of valid data
        (test with invalid data are in test.forms)
        """
        team = TeamFactory()
        data = {
            'team': team.pk,
            'has_signed': 'on',
            'first_name': 'Jane',
            'last_name': 'Doe',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.team_id, team.pk)


class TestProfileUpdateView(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('tasks:update_profile')

    def test_login_required(self):
        self.run_test_login_required()

    def test_profile_required(self):
        self.run_test_profile_required

    def test_get_success_url(self):
        """" should redirect to the home page """
        self.assertEqual(
            ProfileUpdateView(object=ProfileFactory()).get_success_url(),
            reverse('tasks:home')
        )

    def test_valid_update(self):
        """
        checks the profile has been modified accordingly upon submission of valid data
        """
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
        }
        ProfileFactory(user=self.user)
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')


 # ------------------------------------------------
 #               TASKS VIEWS
 # ------------------------------------------------


class TestTaskCreateView(BaseTaskTestCase):
    """ Test Case for the CBV Task Create View """

    def setUp(self):
        super().setUp()
        self.view = TaskCreateView.as_view()
        self.url = reverse("tasks:create_task")

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_not_profile(self):
        self.run_test_profile_required()

    def test_get_success_url(self):
        """" upon success, redirect to tasks:home"""
        self.assertEqual(
            TaskCreateView(object=TaskFactory()).get_success_url(),
            reverse('tasks:home')
        )

    def test_creation(self):
        """ checks a new task has been created upon submission of valid data """
        ProfileFactory(user=self.user)
        data = {
            'name': 'A new task',
            'description': 'just testing',
            'visibility': 1,
            'difficulty': 1,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        task = self.user.created_tasks.first()
        self.assertEqual(task.name, 'A new task')


#  ---------------------------------------------------------------------------
#                       Testing TaskUpdateView
#  ---------------------------------------------------------------------------

class TestTaskUpdateView(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.profile = ProfileFactory(user=self.user)
        self.task = TaskFactory(creator=self.user)
        self.url = reverse("tasks:update_task", kwargs={"pk": self.task.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_redirect_home_if_not_profile(self):
        self.profile.delete()
        self.run_test_profile_required()

    def test_get_success_url(self):
        """" upon success, redirect to tasks:home """
        self.assertEqual(
            TaskUpdateView(object=self.task).get_success_url(),
            reverse('tasks:home')
        )

    def test_successful_update(self):
        """
        posts valid data and checks the Business is updated accordingly
        """
        data = {
            'name': 'Updated name',
            'description': 'Updated testing',
            'visibility': 0,
            'difficulty': 0,
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('tasks:home'), status_code=302, target_status_code=200)
        # We refresh the object from db and check it has been updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated name')

    def test_404_update_task_of_other_people(self):
        """ The user should be denied access to tasks belonging to other users"""
        team2 = TeamFactory(name="other_team")
        profile2 = ProfileFactory(team=team2)
        task2 = TaskFactory(creator=profile2.user)
        self.url = reverse("tasks:update_task", kwargs={"pk": task2.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 404)

    def test_400_update_task_not_new(self):
        """ The user should be denied access to tasks which are no longer new"""
        self.task.status = Task.STATUS.closed
        self.task.save()
        self.url = reverse("tasks:update_task", kwargs={"pk": self.task.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    def test_404_update_task_deleted(self):
        """ The user should be denied access to deleted tasks """
        self.task.is_removed = True
        self.task.save()
        self.url = reverse("tasks:update_task", kwargs={"pk": self.task.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 404)


#  ---------------------------------------------------------------------------
#                       Testing delete_view
#  ---------------------------------------------------------------------------

class TestTaskDeleteView(BaseTaskTestCase):

    def setUp(self):
        super().setUp()
        self.profile = ProfileFactory(user=self.user)
        self.task = TaskFactory(creator=self.user)
        self.url = reverse('tasks:delete_task', kwargs={"pk": self.task.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_successful_update(self):
        """
        posts valid data and checks the task has been destroyed as expected
        """
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse('tasks:home'), status_code=302, target_status_code=200)
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_removed)

    def test_deny_deletion_to_task_of_others(self):
        """
        The user should be denied access to businesses belonging to other users
        """
        team2 = TeamFactory(name="other_team")
        profile2 = ProfileFactory(team=team2)
        task2 = TaskFactory(creator=profile2.user)
        self.url = reverse("tasks:delete_task", kwargs={"pk": task2.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 404)

    def test_deny_deletion_to_task_not_new(self):
        """
        The user should be denied access to businesses belonging to other users
        """
        self.task.status = Task.STATUS.assigned
        self.task.save()
        self.url = reverse("tasks:delete_task", kwargs={"pk": self.task.pk})
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)


#  ---------------------------------------------------------------------------
#                       Testing complete_view
#  ---------------------------------------------------------------------------


class TestTaskCompleteView(BaseTaskTestCase):
    """
    Testing the view used to mark a task as completed -- any visible task can
    be completed by the current user It is closed directly if it belongs to him
    """
    def setUp(self):
        super().setUp()
        self.profile = ProfileFactory(user=self.user)
        team2 = TeamFactory(name="other_team")
        self.profile2 = ProfileFactory(team=team2)
        self.task = TaskFactory(creator=self.profile2.user, status=Task.STATUS.new,
                                visibility=Task.VISIBILITIES.public)
        self.url = reverse('tasks:complete_task', kwargs={"pk": self.task.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_successful_update_same_user(self):
        """
        checks a new task belonging to the same user becomes closed, completed_by properly set and
        the reputation of the current user doesn't increase
        """
        task = TaskFactory(creator=self.user, status=Task.STATUS.new)
        url = reverse('tasks:complete_task', kwargs={"pk": task.pk})
        response = self.client.post(url, {})
        self.assertRedirects(
            response, reverse('tasks:home'), status_code=302, target_status_code=200
        )
        task.refresh_from_db()
        self.assertEqual(task.completed_by, self.user)
        self.assertEqual(task.status, Task.STATUS.closed)
        self.assertEqual(self.user.profile.reputation, 1)

    def test_successful_update_other_user(self):
        """
        checks a new task belonging to another user can be completed and the
        completed_by properly set
        """
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse('tasks:home'), status_code=302,
                             target_status_code=200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS.completed)
        self.assertEqual(self.task.completed_by, self.user)

    @patch('to_do_list.tasks.models.Task.is_visible_by', lambda *_: False)
    def test_deny_completion_for_invisible_task(self):
        """
        The user should be denied access to tasks which are not visible to her
        (we patch Task.is_visible_by, any task should fail)
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    @patch('to_do_list.tasks.models.Task.is_new', lambda *_: False)
    def test_deny_completion_task_not_completed(self):
        """
        Should be impossible to complete tasks which are not new (patc
        Task.is_new so any task should fail)
        """
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)


#  ---------------------------------------------------------------------------
#                       Testing complete_view
#  ---------------------------------------------------------------------------


class TestTaskCloseView(BaseTaskTestCase):
    """
    Test class for the view marking a task as closed
    """

    def setUp(self):
        super().setUp()
        self.profile = ProfileFactory(user=self.user)
        team2 = TeamFactory(name="other_team")
        self.profile2 = ProfileFactory(team=team2)
        self.task = TaskFactory(
            creator=self.user, completed_by=self.profile2.user,
            status=Task.STATUS.completed
        )
        self.url = reverse('tasks:close_task', kwargs={"pk": self.task.pk})

    def test_login_required(self):
        self.run_test_login_required()

    def test_successful_update(self):
        """
        checks a task completed and belonging to the current user can be closed,
        and that the person that completed it has an increase in reputation (exact
        number tested in test_helper_function)
        """
        response = self.client.post(self.url, {})
        self.assertRedirects(response, reverse('tasks:home'), status_code=302,
        target_status_code=200)
        self.task.refresh_from_db()
        self.profile2.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS.closed)
        self.assertTrue(self.profile2.reputation > 1)

    def test_deny_closing_for_task_of_others(self):
        """
        The user should be denied access to tasks belonging to other users
        """
        task2 = TaskFactory(
            creator=self.profile2.user, completed_by=self.user,
            status=Task.STATUS.completed,
            visibility = Task.VISIBILITIES.public
        )
        url = reverse("tasks:close_task", kwargs={"pk": task2.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)

    def test_deny_closing_task_not_completed(self):
        """
        The user should be denied access to tasks belonging to other users
        """
        # Assigned
        self.task.status = Task.STATUS.assigned
        self.task.save()
        url = reverse("tasks:close_task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        # New
        self.task.status = Task.STATUS.new
        self.task.save()
        url = reverse("tasks:close_task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        # closed
        self.task.status = Task.STATUS.new
        self.task.save()
        url = reverse("tasks:close_task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
