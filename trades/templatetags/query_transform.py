from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v

    return updated.urlencode()


@register.simple_tag
def sort_query(request, param, delete_others):
    params = request.GET.copy()

    if delete_others:
        params = { k: v for k, v in params.items() if not k.startswith('sort') or k == param }

    if param in params:
        params[param] = 'asc' if params[param] == 'desc' else 'desc'
    else:
        params[param] = 'desc'
        
    return urlencode(params)

