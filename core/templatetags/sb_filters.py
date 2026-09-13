from django import template
register = template.Library()

@register.filter
def split(value, delimiter=' '):
    return str(value).split(delimiter)

@register.filter
def replace(value, args):
    if ',' in str(args):
        old, new = str(args).split(',', 1)
    else:
        old, new = str(args), ''
    return str(value).replace(old, new)
