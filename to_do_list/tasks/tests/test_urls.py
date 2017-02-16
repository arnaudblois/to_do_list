from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestTasksURLs(TestCase):
    """
    Test URL patterns for tasks app
    """

    def test_create_profile_resolve(self):
        """ /tasks/create-profile/ should resolve to tasks:create_profile """
        self.assertEqual(resolve('/tasks/create-profile/').view_name, 'tasks:create_profile')

    def test_create_profile_reverse(self):
        """ tasks:create_profile should reverse to /tasks/create-profile/ """
        self.assertEqual(
            reverse('tasks:create_profile', kwargs={}),
            '/tasks/create-profile/'
        )

    def test_update_profile_resolve(self):
        """ /tasks/update-profile/ should resolve to tasks:update_profile """
        self.assertEqual(resolve('/tasks/update-profile/').view_name, 'tasks:update_profile')

    def test_update_profile_reverse(self):
        """ tasks:update_profile should reverse to /tasks/update-profile/ """
        self.assertEqual(
            reverse('tasks:update_profile', kwargs={}),
            '/tasks/update-profile/'
        )

    # -------------------
    #   Tasks
    #--------------------

    # New task
    def test_create_task_resolve(self):
        """ /tasks/create-task/ should resolve to tasks:create_task """
        self.assertEqual(resolve('/tasks/create-task/').view_name, 'tasks:create_task')

    def test_create_task_reverse(self):
        """ tasks:create_task should reverse to /tasks/create-task/ """
        self.assertEqual(
            reverse('tasks:create_task', kwargs={}),
            '/tasks/create-task/'
        )

    # Detail task
    def test_detail_task_resolve(self):
        """ /tasks/detail-task/42/ should resolve to tasks:detail_task """
        self.assertEqual(resolve('/tasks/detail-task/42/').view_name, 'tasks:detail_task')

    def test_detail_task_reverse(self):
        """ tasks:detail_task should reverse to /tasks/detail-task/42/ """
        self.assertEqual(
            reverse('tasks:detail_task', kwargs={'pk': 42}),
            '/tasks/detail-task/42/'
        )

    # Update task
    def test_update_task_resolve(self):
        """ /tasks/update-task/42/ should resolve to tasks:update_task """
        self.assertEqual(resolve('/tasks/update-task/42/').view_name, 'tasks:update_task')

    def test_update_task_reverse(self):
        """ tasks:update_task should reverse to /tasks/update-task/42/ """
        self.assertEqual(
            reverse('tasks:update_task', kwargs={'pk': 42}),
            '/tasks/update-task/42/'
        )

    # Complete task
    def test_complete_task_resolve(self):
        """ /tasks/complete-task/42/ should resolve to tasks:complete_tasks """
        self.assertEqual(resolve('/tasks/complete-task/42/').view_name, 'tasks:complete_task')

    def test_complete_task_reverse(self):
        """ tasks:complete_tasks should reverse to /tasks/complete-task/42/ """
        self.assertEqual(
            reverse('tasks:complete_task', kwargs={'pk': 42}),
            '/tasks/complete-task/42/'
        )

    # Close task
    def test_close_task_resolve(self):
        """ /tasks/close-task/42/ should resolve to tasks:close_task """
        self.assertEqual(resolve('/tasks/close-task/42/').view_name, 'tasks:close_task')

    def test_close_task_reverse(self):
        """ tasks:close_task should reverse to /tasks/close-task/42/ """
        self.assertEqual(
            reverse('tasks:close_task', kwargs={'pk': 42}),
            '/tasks/close-task/42/'
        )

    # Delete task
    def test_delete_task_resolve(self):
        """ /tasks/delete-task/42/ should resolve to tasks:delete_tasks """
        self.assertEqual(resolve('/tasks/delete-task/42/').view_name, 'tasks:delete_task')

    def test_delete_task_reverse(self):
        """ tasks:delete_tasks should reverse to /tasks/delete-task/42/ """
        self.assertEqual(
            reverse('tasks:delete_task', kwargs={'pk': 42}),
            '/tasks/delete-task/42/'
        )
