import logging
import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from sqlalchemy.exc import SQLAlchemyError

from triweb.models.user import User

_log = logging.getLogger(__name__)

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
                _log.info(f"User '{user.display_name}' is logged in.")
                update_login_data(request, user)
                headers = remember(request, user.id)
                return HTTPFound(location=came_from, headers=headers)
            message = 'Die Anmeldung hat fehlgeschlagen!'
        except SQLAlchemyError:
            message = 'Es gibt keinen Benutzer mit dieser E-Mail!'
    return dict(message=message, url=request.route_url('login'),
            came_from=came_from, email=email, password=password)

def update_login_data(request, user):
    # Start nested transaction
    nested_transaction = request.dbsession.begin_nested()
    # Update login data
    user.last_login = datetime.datetime.now()
    # Save data to database
    try:
        nested_transaction.commit()
    except SQLAlchemyError as err:
        _log.debug(f'Database: {err}')
        _log.error(f"Unable to update login data for user '{user.display_name}'!")