from triweb.models.user import User
from triweb.models.vehicle import Vehicle
from triweb.models.workday import Workday


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

def get_active_workdays(dbsession):
    #TODO: For simplicity get all workdays for the moment.
    workdays = dbsession.query(Workday).all()
    return workdays

def get_vehicles(dbsession, limit=25):
    return dbsession.query(Vehicle).limit(limit).all()

def get_team_leaders(dbsession, limit=25):
    return dbsession.query(User).\
            filter(User.role.in_(['admin', 'manager', 'team_leader'])).\
            limit(limit).all()
