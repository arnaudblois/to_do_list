# -*- coding: utf-8 -*-

"""Urls for tasks app."""

from django.conf.urls import url

from . import views

urlpatterns = [
    #  Home
    #  ----------------------------------------------------------------------
    url(
        regex=r'^$',
        view=views.home_view,
        name='home'
    ),
    #  Profile urls
    #  ----------------------------------------------------------------------
    url(
        regex=r'^create-profile/$',
        view=views.ProfileCreateView.as_view(),
        name='create_profile'
    ),
    url(
        regex=r'^update-profile/$',
        view=views.ProfileUpdateView.as_view(),
        name='update_profile'
    ),
    #  Task urls
    #  ----------------------------------------------------------------------
    url(
        regex=r'^create-task/$',
        view=views.TaskCreateView.as_view(),
        name='create_task'
    ),
    url(
        regex=r'^detail-task/(?P<pk>[\d]+)/$',
        view=views.TaskDetailView.as_view(),
        name='detail_task'
    ),
    url(
        regex=r'^update-task/(?P<pk>[\d]+)/$',
        view=views.TaskUpdateView.as_view(),
        name='update_task'
    ),
    url(
        regex=r'^complete-task/(?P<pk>[\d]+)/$',
        view=views.complete_task,
        name='complete_task'
    ),
    url(
        regex=r'^close-task/(?P<pk>[\d]+)/$',
        view=views.close_task,
        name='close_task'
    ),
    url(
        regex=r'^delete-task/(?P<pk>[\d]+)/$',
        view=views.delete_task,
        name='delete_task'
    ),
]
