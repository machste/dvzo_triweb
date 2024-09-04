from triweb.models.user import User


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