from importlib import metadata
from pyramid.traversal import DefaultRootFactory
from pyramid.authorization import Allow


class TriWebRoot(DefaultRootFactory):

    APP_VERSION = metadata.version('triweb')

    def __acl__(self):
        return [
            (Allow, 'role:admin', 'administrate'),
            (Allow, 'role:admin', 'manage'),
            (Allow, 'role:manager', 'manage')
        ]

def includeme(config):
    config.set_root_factory(TriWebRoot)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('overview', '/overview')
    config.add_route('issues', '/issues')
    config.add_route('issue', '/issue/{id}')
    config.add_route('calendar', '/calendar')
    config.add_route('users', '/users')
    config.add_route('user_add', '/user/add')
    config.add_route('user_edit', '/user/edit/{id}')
    config.add_route('vehicle_add', '/vehicle/add')
    config.add_route('vehicle_edit', '/vehicle/edit/{id}')
    config.add_route('vehicles', '/vehicles')
    config.add_route('vehicle_manager_add', '/vehicle_manager/add')
    config.add_route('vehicle_manager_edit', '/vehicle_manager/edit/{id}')
    config.add_route('vehicle_managers', '/vehicle_managers')
    config.add_route('workdays', '/workdays')
    config.add_route('workday_add', '/workday/add')
    config.add_route('workday_edit', '/workday/edit/{id}')
    config.add_route('myaccount', '/myaccount')
    config.add_route('settings', '/settings')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('rest.issues', '/rest/issues/{list_name}')
    config.add_route('rest.attachment', '/rest/attachment/{id}')
    config.add_route('rest.workday.poll', '/rest/workday/{id}/poll')
