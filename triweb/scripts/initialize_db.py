import argparse
import sys

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError

from triweb.models.user import User


def setup_users(dbsession):
    """
    Add or update models / fixtures in the database.

    """
    user = User(email='stefan.maechler@gmail.com')
    user.firstname = 'Stefan' 
    user.lastname = 'Mächler'
    user.set_password('ready2start')
    user.role = "admin"
    dbsession.add(user)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', help='Configuration file')
    return parser.parse_args(argv[1:])

def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    try:
        with env['request'].tm:
            dbsession = env['request'].dbsession
            setup_users(dbsession)
    except OperationalError:
        print("Unable to write to database!")
