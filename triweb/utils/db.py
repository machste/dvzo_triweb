from datetime import date, timedelta

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

def get_active_workdays(dbsession, today=None):
    active_wdays = dbsession.query(Workday).\
            filter(Workday.date > date.today() - timedelta(weeks=1)).\
            filter(Workday.state.in_(
                    ['published', 'confirmed', 'done', 'cancelled'])).\
            order_by(Workday.date).all()
    return active_wdays

def get_active_workday_polls(dbsession, user_id=None):
    #TODO: For simplicity get all polls for the moment.
    q = dbsession.query(WorkdayUserPoll)
    if user_id is not None:
        q.filter(WorkdayUserPoll.user_id == user_id)
    return q.all()

def get_vehicles(dbsession, limit=25):
    return dbsession.query(Vehicle).limit(limit).all()

def get_managed_vehicles(dbsession, order=None, limit=25):
    vehicles = dbsession.query(Vehicle).filter(Vehicle.token != None).all()
    # No order is defined return immediately
    if order is None:
        return vehicles
    # Order the vehicles
    ordered_vehicles = []
    for vehicle_type in order:
        for vehicle in vehicles:
            if not isinstance(vehicle, vehicle_type):
                continue
            ordered_vehicles.append(vehicle)
    return ordered_vehicles

def get_team_leaders(dbsession, limit=25):
    return dbsession.query(User).\
            filter(User.role.in_(['admin', 'manager', 'team_leader'])).\
            limit(limit).all()
