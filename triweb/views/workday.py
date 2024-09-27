from datetime import date, time
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.workday import Workday
from triweb.utils.form import Form
from triweb.utils.db import get_manager_display_names, get_engine_display_names
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class WorkdayView(Private):

    @view_config(route_name='workday_add', permission='manage',
            renderer='workday_edit.jinja2')
    def view_add(self):
        mappings = {}
        mappings['action'] = 'add'
        workday = Workday()
        mappings['managers'] = get_manager_display_names(self.dbsession)
        mappings['engines'] = get_engine_display_names(self.dbsession)
        form = WorkdayForm('workday_add')
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(workday)
                self.save_workday(workday)
                self.push_toast('Der neue Arbeitstag wurde erfolgreich hinzugefügt!',
                        title='Arbeitstag erstellt!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('workdays'))
        else:
            # Set default values
            workday.date = date.today()
            workday.start_time = time(9, 0)
            workday.end_time = time(17, 0)
            workday.manager_id = self.request.identity.id
            workday.vehicle_id = None
            workday.cook = False
            form.copy_from(workday)
        mappings['form'] = form
        return mappings

    @view_config(route_name='workday_edit', permission='manage',
            renderer='workday_edit.jinja2')
    def view_edit(self):
        mappings = {}
        mappings['action'] = 'edit'
        workday_id = self.request.matchdict['id']
        workday = self.dbsession.get(Workday, workday_id)
        if workday is None:
            raise DatabaseError(f"Arbeitstag mit ID: '{workday_id}' nicht gefunden!")
        mappings['managers'] = get_manager_display_names(self.dbsession)
        mappings['engines'] = get_engine_display_names(self.dbsession)
        form = WorkdayForm('workday_edit')
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                form.copy_to(workday)
                workday = self.save_workday(workday)
                self.push_toast(f"Der Arbeitstag '{workday.title}' wurde erfolgreich gespeichert!",
                        title='Arbeitstag gespeichert!',
                        type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('workdays'))
        else:
            form.copy_from(workday)
        mappings['form'] = form
        return mappings

    def save_workday(self, workday):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(workday)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return workday


class WorkdayForm(Form):

    FIELDS = [
        'title',
        'date',
        'start_time',
        'end_time',
        'description',
        'manager_id',
        'vehicle_id',
        'cook'
    ]

    def __init__(self, name):
        super().__init__(name, self.FIELDS)

    def copy_from(self, model):
        self.title.value = model.title or ''
        self.date.value = model.date.isoformat()
        self.start_time.value = model.start_time.isoformat(timespec='minutes')
        self.end_time.value = model.end_time.isoformat(timespec='minutes')
        self.description.value = model.description or ''
        self.manager_id.value = model.manager_id
        self.vehicle_id.value = model.vehicle_id or 0
        self.cook.value = model.cook

    def copy_to(self, model):
        model.title = self.title.value
        model.date = date.fromisoformat(self.date.value)
        model.start_time = time.fromisoformat(self.start_time.value)
        model.end_time = time.fromisoformat(self.end_time.value)
        model.description = self.description.value
        model.manager_id = self.manager_id.value
        model.vehicle_id = self.vehicle_id.value
        model.cook = self.cook.value

    def validate(self, params):
        for field in self.validate_each(params):
            if field.name == 'description':
                continue
            if field.name == 'date':
                if date.fromisoformat(field.value) < date.today():
                    field.err_msg = 'Datum liegt in der Vergangenheit!'
                continue
            if field.name == 'end_time':
                start_time = time.fromisoformat(self.start_time.value)
                end_time = time.fromisoformat(field.value)
                if start_time >= end_time:
                    field.err_msg = 'Ungültige Arbeitszeiten!'
            if field.name.endswith('_id'):
                try:
                    field.value = int(field.value)
                except:
                    field.value = 0
                continue
            if field.name == 'cook':
                field.value = field.value is not None
                continue
            if len(field.value) == 0:
                field.err_msg = 'Dieses Feld darf nicht leer sein!'
        return self.is_valid()
