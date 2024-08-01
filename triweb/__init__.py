from pyramid.config import Configurator

from triweb.security import SecurityPolicy
from triweb.session import SessionFactory
from triweb.utils.jinja2.filters import install_jinja2_filters


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.add_jinja2_search_path('triweb:templates')
        config.action(None, install_jinja2_filters, args=(config, ))
        config.set_security_policy(
                SecurityPolicy(secret=settings['auth_cookie.secret']))
        config.set_session_factory(
                SessionFactory(secret=settings['session.secret']))
        config.include('.routes')
        config.include('.models')
        config.scan()
    return config.make_wsgi_app()
