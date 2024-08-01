from wsgiref import headers
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget

@view_config(route_name='logout', renderer='logout.jinja2')
def logout(request):
    if request.identity is None:
        return HTTPFound(location=request.route_url('home'))
    # Get display name of user before forgetting the user
    nickname = request.identity.nickname
    # Forget about the logged in user
    headers = forget(request)
    request.response.headerlist.extend(headers)
    return dict(nickname=nickname)