import os
from datetime import datetime

from django import template
from django.contrib.staticfiles import finders

register = template.Library()


@register.simple_tag
def file_modtime(target_file):
    result = finders.find(target_file)
    if result is None:
        return ''
    file_stat = os.stat(result)
    return datetime.fromtimestamp(file_stat.st_mtime).isoformat()[0:19].replace(":", "-")
