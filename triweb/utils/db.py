from triweb.models.user import User
from triweb.models.vehicle import Vehicle


def get_user_roles(dbsession):
    # Currently this is hardcoded
    return {
        'basic': 'Benutzer',
        'manager': 'Leiter',
        'admin': 'Administrator'
    }

def get_manager_display_names(dbsession, limit=25):
    display_names = {}
    managers = dbsession.query(User).\
            filter(User.role.in_(['admin', 'manager'])).\
            limit(limit).all()
    for manager in managers:
        display_names[manager.id] = manager.display_name
    return display_names

def get_engine_display_names(dbsession, limit=25):
    display_names = {}
    engines = dbsession.query(Vehicle).limit(limit).all()
    for engine in engines:
        display_names[engine.id] = engine.display_name
    return display_names
