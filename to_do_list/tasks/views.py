# -*- coding: utf-8 -*-

"""Views for tasks app."""

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.views.generic import (
    DetailView,
    UpdateView,
    CreateView,
    FormView,
)

from django.http.response import (
    HttpResponseNotAllowed,
    HttpResponseRedirect,
    JsonResponse,
)

from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.urls.base import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

from .forms import UserProfileForm, UserUpdateForm
from .models import Profile, Task
from .tables import TaskFilter, TaskFilterFormHelper, TaskTable
from .helper_functions import give_reputation_reward
from django_tables2 import RequestConfig


#  ----------------------------------------------------
#              Profile Views
#  ----------------------------------------------------


@login_required
def home_view(request):
    """
    Return the home view after successful login. By default, lists all tasks
    visible by the current user.
    Provides also a filter by status and difficulty.
    """

    try:
        profile = Profile.objects.get(user=request.user)
        VIZ = Task.VISIBILITIES
        queryset = Task.objects.select_related().filter(is_removed=False).filter(
            Q(visibility=VIZ.public) | Q(creator=request.user) |
            Q(visibility=VIZ.team_only, creator__profile__team_id=request.user.profile.team_id)
        )
        f = TaskFilter(request.GET, queryset=queryset)
        f.form.helper = TaskFilterFormHelper()
        table = TaskTable(f.qs, user=request.user)
        RequestConfig(request, paginate={"per_page": 10, "page": 1}).configure(table)
    except Profile.DoesNotExist:
        profile, table, f = None, None, None

    context = {"profile": profile, 'table': table, 'filter': f, "request": request}
    if request.is_ajax():
        html = render_to_string("tasks/table_home.html", context)
        return JsonResponse({'html': html})
    else:
        return render(request, "tasks/table_home.html", context)


class ProfileCreateView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    """
    CBV view to activate the user's profile, accept the Terms & Conditions
    and set her team. Instantiate a UserProfileForm, an hybrid form to update
    both first_name and last_name and the profile info at the same time.
    """

    template_name = 'tasks/create_profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('tasks:home')
    success_message = _("You're all set, you are now able to use all our features!")

    def dispatch(self, request, *args, **kwargs):
        """If the user is already activated, redirect to tasks:home."""
        if Profile.objects.filter(user_id=self.request.user.id).exists():
            return HttpResponseRedirect(reverse('tasks:home'))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        data = self.request.POST if self.request.method == "POST" else None
        return self.form_class(data=data, user=self.request.user)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProfileRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin which verifies that the current user is authenticated and
    has a profile.
    """
    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = Profile.objects.get(user_id=self.request.user.id)
        except Profile.DoesNotExist:
            messages.error(request, _("You must have a valid profile to access this page"))
            return HttpResponseRedirect(reverse('tasks:home'))
        return super().dispatch(request, *args, **kwargs)


class ProfileUpdateView(SuccessMessageMixin, ProfileRequiredMixin, UpdateView):
    """
    CBV view to update the user first and last-names based on UserUpdateForm.
    """
    template_name = 'tasks/update_profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('tasks:home')
    success_message = _("Your profile has been successfully updated")

    def get_object(self):
        """Return the current user."""
        return self.request.user


#  ----------------------------------------------------
#              Task Views
#  ----------------------------------------------------


class TaskCreateView(SuccessMessageMixin, ProfileRequiredMixin, CreateView):
    """CBV creating a new task for the current user."""

    model = Task
    fields = ['name', 'description', 'visibility', 'difficulty']
    success_message = _("Your task has been successfully created.")
    success_url = reverse_lazy('tasks:home')
    template_name = "tasks/create_task_form.html"

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.save()
        return super().form_valid(form)


class TaskUpdateView(SuccessMessageMixin, ProfileRequiredMixin, UpdateView):
    """
    CBV to update an existing task -- only possible if the task has
    not been assigned/completed and belongs to the user.
    """

    model = Task
    fields = ['name', 'description', 'visibility', 'difficulty']
    success_message = _("Your task has been successfully updated.")
    success_url = reverse_lazy('tasks:home')
    template_name = "tasks/update_task_form.html"

    def get_object(self):
        """
        Only get the Task record for the user making the request and only if it
        is not assigned.
        """
        task = get_object_or_404(Task, creator=self.request.user,
                                 is_removed=False, pk=self.kwargs['pk'])
        if task.status != Task.STATUS.new:
            raise SuspiciousOperation(_('You cannot edit a task modified by other people'))
        return task


class TaskDetailView(ProfileRequiredMixin, DetailView):
    """
    CBV to see the details of an existing task -- task has to be visible to
    the current user.
    """

    model = Task
    template_name = "tasks/detail_task.html"
    queryset = Task.objects.filter(is_removed=False)

    def get_object(self):
        """Only gets the Task record if the current user can see it."""
        task = get_object_or_404(Task, is_removed=False, pk=self.kwargs['pk'])
        if not task.is_visible_by(self.request.user):
            raise SuspiciousOperation(_('You cannot see this tasks'))
        return task


@login_required
def complete_task(request, pk):
    """
    Mark a task as completed -- if task belongs to current user, it is then
    automatically closed as well.
    """

    home_url = reverse('tasks:home')
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if not Profile.objects.filter(user=request.user).exists():
        return HttpResponseRedirect(home_url)

    task = get_object_or_404(Task, pk=pk, is_removed=False)
    if not task.is_visible_by(request.user) or not task.is_new():
        raise SuspiciousOperation(_("You do not have the right to complete this task"))

    task.status = Task.STATUS.closed if request.user == task.creator else Task.STATUS.completed
    task.completed_by = request.user
    task.save()
    return JsonResponse({}) if request.is_ajax() else HttpResponseRedirect(home_url)


@login_required
def close_task(request, pk):
    """
    Mark a task as closed -- only the creator can do this on tasks completed by
    another user. Gives a reputation reward to the person that performed the
    task.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    task = get_object_or_404(Task, creator=request.user, pk=pk, is_removed=False)
    if task.status != Task.STATUS.completed:
        raise SuspiciousOperation(_("You do not have the right to complete this task"))
    give_reputation_reward(task)
    task.status = Task.STATUS.closed
    task.save()
    return JsonResponse({}) if request.is_ajax() else HttpResponseRedirect(reverse('tasks:home'))


@login_required
def delete_task(request, pk):
    """
    [POST only] deletes the task whose pk is in url if it belongs to the
    current user and is new.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    task = get_object_or_404(Task, creator=request.user, pk=pk, is_removed=False)
    if not task.is_new():
        raise SuspiciousOperation(_("You do not have the right to delete this task"))
    task.is_removed = True
    task.save()
    return JsonResponse({}) if request.is_ajax() else HttpResponseRedirect(reverse('tasks:home'))
