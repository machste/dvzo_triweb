from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from sqlalchemy.exc import SQLAlchemyError

from triweb.models.user import User

@view_config(route_name='login', renderer='login.jinja2')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)
    message = ''
    email = ''
    password = ''
    if 'form.submitted' in request.params:
        email = request.params['email']
        password = request.params['password']
        # Get user information from database
        try:
            query = request.dbsession.query(User)
            user = query.filter(User.email == email).one()
            if user.check_password(password):
                headers = remember(request, user.id)
                return HTTPFound(location=came_from, headers=headers)
            message = 'Die Anmeldung hat fehlgeschlagen!'
        except SQLAlchemyError:
            message = 'Es gibt keinen Benutzer mit dieser E-Mail!'
    return dict(message=message, url=request.route_url('login'),
            came_from=came_from, email=email, password=password)
