# -*- coding: utf-8 -*-

"""
Helper functions for the tasks app: calculate_reputation_gain and
give_reputation_reward.
"""

from .models import Profile, Task
from django.db.models import F


def calculate_reputation_gain(task):
    """
    Calculate the reputation gained by completing a task. Currently based on
    difficulty only.
    """
    DIFF = Task.DIFFICULTIES
    d = task.difficulty
    if d == DIFF.trivial:
        return 1
    if d == DIFF.easy:
        return 5
    if d == DIFF.OK:
        return 10
    if d == DIFF.hard:
        return 25
    if d == DIFF.heroic:
        return 100
    if d == DIFF.nightmare:
        return 500


def give_reputation_reward(task):
    """
    Add the reputation reward to the profile of the user who completed the
    task.
    """
    reward = calculate_reputation_gain(task)
    profile = Profile.objects.get(user=task.completed_by)
    profile.reputation = F('reputation') + reward
    profile.save()
