from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import Vehicle, SteamLoco, ElectricLoco, DieselLoco
from triweb.utils.form import Form
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class VehicleView(Private):

    @view_config(route_name='vehicle_state', permission='lead',
            renderer='vehicle_state.jinja2')
    def view(self):
        vehicle_id = self.request.matchdict['id']
        vehicle = self.dbsession.get(Vehicle, vehicle_id)
        if vehicle is None:
            raise DatabaseError(f"Fahrzeug mit ID: '{vehicle_id}' nicht gefunden!")
        if isinstance(vehicle, SteamLoco):
            form = SteamLocoForm(Vehicle.STATES)
        elif isinstance(vehicle, ElectricLoco):
            form = ElectricLocoForm(Vehicle.STATES)
        elif isinstance(vehicle, DieselLoco):
            form = DieselLocoForm(Vehicle.STATES)
        else:
            raise DatabaseError(f"Fahrzeugtype '{vehicle.TYPE}' wird nicht unterstützt!")
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(vehicle)
                self.save_vehicle(vehicle)
                self.push_toast(f'Der Status der {vehicle.display_name} wurde erfolgreich aktualisiert!',
                        title='Status aktualisiert!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('overview'))
        else:
            form.copy_from(vehicle)
        return dict(loco=vehicle, form=form)

    def save_vehicle(self, vehicle):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(vehicle)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return vehicle


class VehicleForm(Form):

    def __init__(self, name, states):
        super().__init__(name)
        self.add_field(Form.Select('state', states))
        self.add_field(Form.TextField('station', allow_empty=True))
        self.add_field(Form.TextField('track', allow_empty=True))
        self.add_field(Form.TextField('space', allow_empty=True))


class SteamLocoForm(VehicleForm):

    def __init__(self, states):
        super().__init__('steam_loco', states)
        self.add_field(Form.Checkbox('boiler_emtpy'))
        self.add_field(Form.Checkbox('check_leakage'))


class ElectricLocoForm(VehicleForm):

    def __init__(self, states):
        super().__init__('electric_loco', states)


class DieselLocoForm(VehicleForm):

    def __init__(self, states):
        super().__init__('diesel_loco', states)
        self.add_field(Form.Checkbox('low_fuel'))
