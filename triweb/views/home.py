from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='home')
def home(request):
    # For the moment this web site has no home page, redirect to overview
    return HTTPFound(location=request.route_url('overview'))
