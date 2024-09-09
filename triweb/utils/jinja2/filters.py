from markupsafe import Markup
from markdown import markdown

def prefix(value, prefix):
    if value is not None and len(value) > 0:
        return f'{prefix}{value}'
    return ''

def postfix(value, postfix):
    if value is not None and len(value) > 0:
        return f'{value}{postfix}'
    return ''

def md_to_html(value):
    return Markup(markdown(value))


def install_jinja2_filters(config):
    env = config.get_jinja2_environment()
    env.filters['prefix'] = prefix
    env.filters['postfix'] = postfix
    env.filters['md_to_html'] = md_to_html
