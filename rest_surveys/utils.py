from __future__ import unicode_literals
import django, importlib


def remote_field(field):
    """
    https://docs.djangoproject.com/en/1.9/releases/1.9/#field-rel-changes

    Function from django-filter 0.14.0. Future versions of django-filters don't
    support Django 1.7, so we're sticking with django-filter 0.11.0 for now.
    """
    if django.VERSION >= (1, 9):
        return field.remote_field
    return field.rel

def get_field_names(model, field_types=None):
    """
    Return a list of `model`'s fields.
    """
    opts = model._meta

    if field_types is not None:
        return [
            f.name for f in (opts.fields + opts.many_to_many)
            if not (getattr(remote_field(f), 'parent_link', False)) and
            f.__class__ in field_types
        ]

    return [
        f.name for f in (opts.fields + opts.many_to_many)
        if not (getattr(remote_field(f), 'parent_link', False))
    ]

def to_class(class_str):
    if not class_str:
        return None

    module_bits = class_str.split('.')
    module_path, class_name = '.'.join(module_bits[:-1]), module_bits[-1]
    module = importlib.import_module(module_path)
    return getattr(module, class_name, None)
