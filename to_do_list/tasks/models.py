# -*- coding: utf-8 -*-

"""Models for tasks app: Team, Profile, Tasks."""

from django.db.models import (
    Model, ForeignKey, CharField, BooleanField, OneToOneField, DateTimeField,
    ManyToManyField, PositiveIntegerField, PositiveSmallIntegerField,
)

from model_utils import Choices
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django.conf import settings
USER_MODEL = settings.AUTH_USER_MODEL


# ----------------------------------------------------------------------------
#                           Profile and Team
# -----------------------------------------------------------------------------


class Team(Model):
    """
    User must belong to a Team. This is useful to determine access rights and
    making possible to add collaborative / competitive features in future.
    """

    name = CharField(max_length=64)

    def __str__(self):
        return "{0}".format(self.name)

    class Meta:
        unique_together = (("name",),)


class Profile(Model):
    """
    Profile of the users, linked one-to-one with User
    - Requires the consent with the terms and conditions and choosing a Team
    """

    user = OneToOneField(USER_MODEL, primary_key=True)
    has_signed = BooleanField(default=False)
    team = ForeignKey(Team)
    reputation = PositiveIntegerField(default=1)

    def __str__(self):
        """Convert to str"""
        return "{0}'s profile".format(self.user.username)


# ----------------------------------------------------------------------------
#                           Tasks
# ----------------------------------------------------------------------------


# Choices for status, defined here as used by both Task and TaskStatusHistory
task_choices = Choices(
    (0, 'new', _('new')),
    (1, 'assigned', _('assigned')),
    (2, 'completed', _('completed')),
    (3, 'closed', _('closed')),
)


class Task(Model):
    """
    Model for the tasks of the to_do_list
    Contains a name, description, creator, difficulty (used to calculate
    reputation), 'Completed_by' records the user who marked it as done
    Followers and assignment are not implemented yet.
    """

    STATUS = task_choices
    name = CharField(max_length=64)
    description = CharField(max_length=128)
    VISIBILITIES = Choices(
        (0, 'private', _('private')), (1, 'team_only', _('team only')),
        (2, 'public', _('public')),
    )
    visibility = PositiveSmallIntegerField(
        choices=VISIBILITIES, default=VISIBILITIES.public
    )
    created_at = DateTimeField(default=timezone.now, blank=True, null=True)
    creator = ForeignKey(USER_MODEL, related_name='created_tasks')
    followers = ManyToManyField(USER_MODEL)
    is_removed = BooleanField(default=False)
    assigned_to = ForeignKey(USER_MODEL, null=True, blank=True, related_name='assigned_tasks')
    completed_by = ForeignKey(USER_MODEL,  null=True, blank=True, related_name='completed_tasks')
    status = PositiveSmallIntegerField(choices=STATUS, default=STATUS.new)
    DIFFICULTIES = Choices(
        (0, 'trivial', _('trivial')), (1, 'easy', _('easy')),
        (2, 'OK', _('OK')), (3, 'hard', _('hard')),
        (4, 'heroic', _('heroic')), (5, 'nightmare', _('nightmare')),
    )
    difficulty = PositiveSmallIntegerField(
        choices=DIFFICULTIES, default=DIFFICULTIES.OK
    )

    def __str__(self):
        return self.name

    def is_new(self):
        """Shortcut function - returns a Boolean True if status is new."""
        return self.status == Task.STATUS.new

    def is_visible_by(self, user):
        """Return whether a task is visible by a given user."""
        VIZ = Task.VISIBILITIES
        return (
            self.visibility == VIZ.public or self.creator == user or
            (self.visibility == VIZ.team_only and self.creator.profile.team_id == user.profile.team_id)
        )


# class TaskStatusHistory(Model):
#     """
#     Feature to add: class keeping track of the status history for a task
#     """
#     STATUS = task_choices
#     task = ForeignKey(Task)
#     status = PositiveSmallIntegerField(choices=STATUS)
#     modified_at = DateTimeField(default=timezone.now, blank=True, null=True)
#
#     def __str__(self):
#         return "{1} {0} for {2}".format(self.amount, self.currency,
#                                         self.business)
#
#     class Meta:
#         verbose_name_plural = "task_status_histories"
