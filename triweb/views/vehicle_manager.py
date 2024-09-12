from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy.orm import make_transient
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.user import User
from triweb.models.vehicle import Vehicle, VehicleManager
from triweb.utils.form import Form
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class VehicleManagerView(Private):

    def __init__(self, request):
        super().__init__(request)
        self.vehicles = self.get_vehicles()
        self.prev_vmanager_user_id = None

    @view_config(route_name='vehicle_manager_add', permission="administrate",
            renderer='vehicle_manager_edit.jinja2')
    def view_add(self):
        mappings = {}
        mappings['action'] = 'add'
        vmanager = VehicleManager()
        team_leaders = self.get_team_leaders(only_available=True)
        form = VehicleManagerForm('add', team_leaders, self.vehicles)
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(vmanager)
                self.save_vehicle_manager(vmanager)
                self.push_toast(f"Der Lok-Götti '{vmanager.display_name}' wurde erfolgreich hinzugefügt!",
                        title='Lok-Götti erstellt!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('vehicle_managers'))
        else:
            # Set default values
            vmanager.badge_color = '#808080'
            form.copy_from(vmanager)
        mappings['form'] = form
        return mappings

    @view_config(route_name='vehicle_manager_edit', permission='administrate',
            renderer='vehicle_manager_edit.jinja2')
    def view_edit(self):
        mappings = {}
        mappings['action'] = 'edit'
        vmanager_id = self.request.matchdict['id']
        vmanager = self.dbsession.get(VehicleManager, vmanager_id)
        if vmanager is None:
            raise DatabaseError(f"Lok-Götti mit ID: '{vmanager_id}' nicht gefunden!")
        self.prev_vmanager_user_id = vmanager.user_id
        team_leaders = self.get_team_leaders()
        # Add the current vehicle manager
        form = VehicleManagerForm('edit', team_leaders, self.vehicles)
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                with self.dbsession.no_autoflush:
                    form.copy_to(vmanager)
                vmanager = self.save_vehicle_manager(vmanager)
                self.push_toast(f"Lok-Götti '{vmanager.display_name}' wurde erfolgreich gespeichert!",
                        title='Lok-Götti gespeichert!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('vehicle_managers'))
        else:
            form.copy_from(vmanager)
        mappings['form'] = form
        return mappings

    def get_vehicles(self, limit=25):
        return self.dbsession.query(Vehicle).limit(limit).all()

    def get_team_leaders(self, only_available=False, limit=25):
        team_leaders = self.dbsession.query(User).\
                filter(User.role.in_(['admin', 'manager', 'team_leader'])).\
                limit(limit).all()
        if not only_available:
            return team_leaders
        available_team_leaders = []
        vmanagers = self.dbsession.query(User).join(VehicleManager).all()
        for team_leader in team_leaders:
            is_already_vmanager = False
            for vmanager in vmanagers:
                if team_leader.id == vmanager.id:
                    is_already_vmanager = True
                    break
            if not is_already_vmanager:
                available_team_leaders.append(team_leader)
        return available_team_leaders

    def save_vehicle_manager(self, vmanager):
        violated_vmanager = None
        # Check if the desired user is avalable.
        if self.prev_vmanager_user_id is not None \
                and self.prev_vmanager_user_id != vmanager.user_id:
            with self.dbsession.no_autoflush:
                violated_vmanager = self.dbsession.query(VehicleManager).\
                        filter(VehicleManager.user_id == vmanager.user_id).\
                        one_or_none()
            if violated_vmanager is not None:
                # The disired user violates an other vehicle manager, it has
                # to be removed temporalily from the session.
                self.dbsession.expunge(vmanager)
        # Save the vehicle manager
        nested_transaction = self.dbsession.begin_nested()
        try:
            if violated_vmanager is not None:
                # Temporarily remove violated user
                self.dbsession.delete(violated_vmanager)
                self.dbsession.flush()
                # Add the changes vehicle manager back to the session
                self.dbsession.add(vmanager)
                # Exchange the user of the violated vehicle manager ...
                violated_vmanager.user_id = self.prev_vmanager_user_id
                # ... and add it back to the session
                make_transient(violated_vmanager)
                self.dbsession.add(violated_vmanager)
            else:
                self.dbsession.add(vmanager)
            # Finally commit everthing
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        self.dbsession.expire(vmanager)
        return vmanager


class VehicleManagerForm(Form):

    def __init__(self, name, team_leaders, vehicles):
        super().__init__(f'vehicle_manager_{name}')
        self.add_field(Form.SelectId('user_id', team_leaders))
        self.add_field(Form.ColorField('badge_color'))
        self.add_field(Form.SelectMultipleIds(
                'vehicles', vehicles, allow_empty=True))
