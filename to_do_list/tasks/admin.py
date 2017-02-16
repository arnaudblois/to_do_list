# -*- coding: utf-8 -*-

"""Admin module for task -- profile, task and team."""

from django.contrib import admin
from .models import (
    Profile, Task, Team,
)


class ProfileAdmin(admin.ModelAdmin):
    """Admin class for profiles."""

    pass


class TaskAdmin(admin.ModelAdmin):
    """Admin class for tasks."""

    pass


class TeamAdmin(admin.ModelAdmin):
    """Admin class for teams."""

    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Team, TeamAdmin)
