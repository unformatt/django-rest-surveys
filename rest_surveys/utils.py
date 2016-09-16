from __future__ import unicode_literals
import django
from django.db import models


def remote_field(field):
    """
    https://docs.djangoproject.com/en/1.9/releases/1.9/#field-rel-changes

    Function from django-filter 0.14.0. Future versions of django-filters don't
    support Django 1.7, so we're sticking with django-filter 0.11.0 for now.
    """
    if django.VERSION >= (1, 9):
        return field.remote_field
    return field.rel

def get_all_model_fields(model, field_types=None):
    """
    Function from django-filter 0.14.0. Future versions of django-filters don't
    support Django 1.7, so we're sticking with django-filter 0.11.0 for now.
    """
    opts = model._meta

    if field_types is not None:
        return [
            f.name for f in sorted(opts.fields + opts.many_to_many)
            if not isinstance(f, models.AutoField) and
            not (getattr(remote_field(f), 'parent_link', False)) and
            f.__class__ in field_types
        ]

    return [
        f.name for f in sorted(opts.fields + opts.many_to_many)
        if not isinstance(f, models.AutoField) and
        not (getattr(remote_field(f), 'parent_link', False))
    ]
