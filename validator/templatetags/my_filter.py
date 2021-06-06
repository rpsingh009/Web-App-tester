from django import template

from django.core.files.storage import default_storage
register = template.Library()

@register.filter
def replace_newline(string):
	return string.replace('\n', ' ')


@register.filter(name='file_exists')
def file_exists(filepath):
    if default_storage.exists(filepath):
        return 1
    else:
        return 0