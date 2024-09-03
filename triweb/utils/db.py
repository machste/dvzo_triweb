def get_user_roles(dbsession):
    # Currently this is hardcoded
    return {
        'basic': 'Benutzer',
        'manager': 'Leiter',
        'admin': 'Administrator'
    }