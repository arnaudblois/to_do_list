# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """
    Workaround for international user names in Django <1.10
    Django 1.10 introduced utf-8 support for first_name and last_name
    """

    name = models.CharField(_('Name of User'), blank=True, max_length=255)

    def __str__(self):
        return self.username
