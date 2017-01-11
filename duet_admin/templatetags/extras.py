import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
   return field.as_widget(attrs={"class":css})

@register.filter(name='keyvalue')
def keyvalue(dict, key):
    return dict[key]

@register.simple_tag
def active_url(request, view_name):
    from django.core.urlresolvers import resolve, Resolver404
    if not request:
        return ""
    try:
        return "active" if resolve(request.path_info).url_name == view_name else ""
    except Resolver404:
        return ""