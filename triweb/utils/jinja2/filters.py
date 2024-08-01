def prefix(value, prefix):
    if value is not None and len(value) > 0:
        return f'{prefix}{value}'
    return ''

def install_jinja2_filters(config):
    env = config.get_jinja2_environment()
    env.filters['prefix'] = prefix
