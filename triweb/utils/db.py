from triweb.models.user import User
from triweb.models.vehicle import Vehicle
from triweb.models.workday import Workday
from triweb.models.workday_user_poll import WorkdayUserPoll


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

def get_active_workday_polls(dbsession, user_id=None):
    #TODO: For simplicity get all polls for the moment.
    q = dbsession.query(WorkdayUserPoll)
    if user_id is not None:
        q.filter(WorkdayUserPoll.user_id == user_id)
    return q.all()

def get_vehicles(dbsession, limit=25):
    return dbsession.query(Vehicle).limit(limit).all()

def get_team_leaders(dbsession, limit=25):
    return dbsession.query(User).\
            filter(User.role.in_(['admin', 'manager', 'team_leader'])).\
            limit(limit).all()
