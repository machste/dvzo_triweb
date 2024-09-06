from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import (forbidden_view_config, notfound_view_config,
        exception_view_config)

from triweb.errors import GeneralError

@forbidden_view_config(renderer='triweb:templates/errors/403.jinja2')
def forbidden_view(request):
    if request.identity is None:
        next_url = request.route_url('login', _query={'next_url': request.url})
        return HTTPSeeOther(location=next_url)
    request.response.status = 403
    return {}

@notfound_view_config(renderer='triweb:templates/errors/404.jinja2')
def notfound_view(request):
    request.response.status = 404
    return {}

@exception_view_config(GeneralError,
        renderer='triweb:templates/errors/500.jinja2')
def generror_view(exc, request):
    request.response.status = 500
    return dict(topic=exc.topic, message=str(exc))
