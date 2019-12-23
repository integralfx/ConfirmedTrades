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

    if param in params:
        params[param] = 'asc' if params[param] == 'desc' else 'desc'
    else:
        # Initially, the home page is already sorted by the user but doesn't have the 'sort-user=asc' query. Clicking on
        # it in this case, should sort the users in descending order.
        # However, changing the sorted column should sort in ascending order. For example, say the get query is 
        # 'sort-trades=asc'. Clicking on the user column would result in 'sort-user=asc'.
        sort_desc = param == 'sort-user' and 'sort-user' not in params and 'sort-trades' not in params
        params[param] = 'desc' if sort_desc else 'asc'

    if delete_others:
        params = { k: v for k, v in params.items() if not k.startswith('sort') or k == param }
        
    return urlencode(params)


@register.simple_tag
def get_param(request, param):
    params = request.GET.copy()
    return params[param] if param in params else None