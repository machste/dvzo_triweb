from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models import Vehicle, User, VehicleManager
from triweb.utils.form import Form
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class VehicleView(Private):

    @view_config(route_name='vehicle_add', permission='manage',
            renderer='vehicle_edit.jinja2')
    def view_add(self):
        mappings = {}
        mappings['action'] = 'add'
        vehicle = Vehicle()
        mappings['managers'] = self.get_vehicle_managers()
        form = VehicleForm('vehicle_add')
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(vehicle)
                self.save_vehicle(vehicle)
                self.push_toast('Das neue Fahrzeug wurde erfolgreich hinzugefügt!',
                        title='Fahrzeug erstellt!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('vehicles'))
        mappings['form'] = form
        return mappings

    @view_config(route_name='vehicle_edit', permission='manage',
            renderer='vehicle_edit.jinja2')
    def view_edit(self):
        mappings = {}
        mappings['action'] = 'edit'
        vehicle_id = self.request.matchdict['id']
        vehicle = self.dbsession.get(Vehicle, vehicle_id)
        if vehicle is None:
            raise DatabaseError(f"Fahrzeug mit ID: '{vehicle_id}' nicht gefunden!")
        mappings['managers'] = self.get_vehicle_managers()
        form = VehicleForm('vehicle_edit')
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(vehicle)
                vehicle = self.save_vehicle(vehicle)
                self.push_toast(f"Das Fahrzeug '{vehicle.display_name}' wurde erfolgreich gespeichert!",
                        title='Fahrzeug gespeichert!',
                        type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('vehicles'))
        else:
            form.copy_from(vehicle)
        mappings['form'] = form
        return mappings

    def get_vehicle_managers(self, limit=25):
        dnames = { 0: '---' }
        vmanagers = self.dbsession.query(VehicleManager).\
                join(User).all()
        for vm in vmanagers:
            dnames[vm.id] = vm.user.display_name
        return dnames

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

    FIELDS = [
        'vname',
        'number',
        'nvr',
        'token',
        'given_name',
        'short_name',
        'manager_id'
    ]

    def __init__(self, name):
        super().__init__(name, self.FIELDS)

    def copy_from(self, model):
        self.vname.value = model.name
        self.number.value = model.number
        self.nvr.value = model.nvr or ''
        self.token.value = model.token or ''
        self.given_name.value = model.given_name or ''
        self.short_name.value = model.short_name or ''
        self.manager_id.value = model.manager_id or 0

    def copy_to(self, model):
        model.name = self.vname.value
        model.number = self.number.value if self.number.value > 0 else None
        str_or_none = lambda x: x if len(x) > 0 else None
        model.nvr = str_or_none(self.nvr.value)
        model.token = str_or_none(self.token.value)
        model.given_name = str_or_none(self.given_name.value)
        model.short_name = str_or_none(self.short_name.value)
        model.manager_id = self.manager_id.value

    def validate(self, params):
        for field in self.validate_each(params):
            if field.name in ('nvr', 'token', 'given_name', 'short_name'):
                continue
            if field.name == 'number':
                try:
                    field.value = int(field.value)
                except:
                    field.err_msg = 'Bitte gib eine gültige Fahrzeugnummer ein!'
                continue
            if field.name.endswith('_id'):
                try:
                    field.value = int(field.value)
                except:
                    field.value = 0
                continue
            if len(field.value) == 0:
                field.err_msg = 'Dieses Feld darf nicht leer sein!'
        return self.is_valid()
