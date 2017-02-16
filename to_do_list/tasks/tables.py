"""
Tables module -- containing the TaskTable which manages the list displayed
on the tasks:home page, and the related TaskFilter and helperto filter these
tasks using crispy forms.
"""

import django_filters
import django_tables2 as tables
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.html import mark_safe, format_html
from .models import Task


class TaskTable(tables.Table):
    """
    Class dealing with the creation of the tasks table located on the task home
    page.
    """

    action = tables.Column(empty_values=(), orderable=False)
    pk = tables.Column(visible=False)

    def __init__(self, *args, **kwargs):
        """
        Retrieve the current user to display the tasks belonging to her
        differently.
        """

        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def render_name(self, record, value):
        """
        Add the link to details, strikethrough the name if status is done,
        boldface if current user is the creator.
        """

        detail_url = reverse('tasks:detail_task', kwargs={'pk': record.pk})
        value = format_html('<a href="{}">{}</a>', detail_url, value)
        if record.creator == self.user:
            value = format_html("<b>{}</b>", value)
        if record.status == Task.STATUS.completed or record.status == Task.STATUS.closed:
            value = format_html("<del>{}</del>", value)
        return value

    def render_action(self, record):
        """
        Provide a few shortcut attributes and pass it to actions_cell for
        formatting.
        """
        record.is_editable = record.creator == self.user and record.status == Task.STATUS.new
        record.can_be_closed = record.creator == self.user and record.status == Task.STATUS.completed
        record.can_be_completed = record.status == Task.STATUS.new
        return render_to_string('tasks/actions_cell.html', {'record': record})

    class Meta:
        model = Task
        fields = ['pk', 'name', 'creator', 'visibility', 'difficulty', 'status']
        empty_text = _("There are no task matching the search criteria...")


class TaskFilter(django_filters.FilterSet):
    """A filterset to filter tasks by visibility and status."""

    class Meta:
        model = Task
        fields = ['visibility', 'status']


class TaskFilterFormHelper(FormHelper):
    """
    Helper class enabling crispy_form to typeset the filter form correctly.
    """

    form_class = 'form-inline'
    form_method = 'GET'
    layout = Layout(
           Field('visibility'),
           Field('status'),
           Submit('submit', _('Filter'), css_class='btn btn-default'),
    )
    form_id = 'filter-form'
