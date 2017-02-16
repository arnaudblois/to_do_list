# -*- coding: utf-8 -*-

"""Form modules for tasks app."""

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Profile, Task
from to_do_list.users.models import User


class UserUpdateForm(forms.ModelForm):
    """
    Form updating the first and last names of a user.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    """
    Form creating a user Profile
    """

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["has_signed"].required = True
        self.fields["has_signed"].label = _("""
            By ticking this box, you agree with our terms and conditions
            (tldr; todolist.ovh is just a demo project and comes with no
            guarantee.
            """)
        self.fields["team"].attrs = {'title': _("""
            Please select a team. Choose wisely your faction as this can't be
            changed later on.
            """)}

    def save(self):
        """Attach the related user to the profile."""
        instance = super().save(commit=False)
        instance.user = self.user
        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = ['has_signed', 'team']


class UserProfileForm:
    """
    Object quacking like a Form wrapping a user_form and a profile_form.
    """

    def __init__(self, user, borrower=None, data=None, *args, **kwargs):
        self.profile_form = ProfileForm(
            instance=borrower, user=user, data=data
        )
        self.user_form = UserUpdateForm(instance=user, data=data)

    def is_valid(self):
        """
        calls the is_valid method of both forms and assign to self a
        cleaned_data attribute (useful to use SuccessMessageMixin)
        """
        profile_form_is_valid = self.profile_form.is_valid()
        user_form_is_valid = self.user_form.is_valid()
        is_valid = profile_form_is_valid and user_form_is_valid
        self.cleaned_data = self.profile_form.cleaned_data
        self.cleaned_data.update(self.user_form.cleaned_data)
        return is_valid

    def save(self):
        self.user_form.save()
        self.profile_form.save()
