from datetime import date, time
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther, HTTPForbidden
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.workday import Workday
from triweb.utils import db
from triweb.utils.form import Form
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class WorkdayView(Private):

    def __init__(self, request):
        super().__init__(request)
        self.team_leaders = db.get_team_leaders(self.dbsession)
        self.vehicles = db.get_vehicles(self.dbsession)

    @view_config(route_name='workday.add', permission='lead',
            renderer='workday_edit.jinja2')
    def view_add(self):
        workday = Workday()
        form = WorkdayForm('add', self.team_leaders, self.vehicles)
        form.date.allow_past = False
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
        return dict(action='add', form=form)

    @view_config(route_name='workday.edit', permission='lead',
            renderer='workday_edit.jinja2')
    def view_edit(self):
        workday_id = self.request.matchdict['id']
        workday = self.dbsession.get(Workday, workday_id)
        if workday is None:
            raise DatabaseError(f"Arbeitstag mit ID: '{workday_id}' nicht gefunden!")
        # Check ownership for permissions less than manager
        if not self.request.has_permission('manage') \
                and self.request.identity.id != workday.manager_id:
            raise HTTPForbidden()
        form = WorkdayForm('edit', self.team_leaders, self.vehicles)
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
        return dict(action='edit', form=form)

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

    def __init__(self, name, team_leaders, vehicles):
        super().__init__(f'workday_{name}')
        self.add_field(Form.TextField('title'))
        self.add_field(Form.DateField('date'))
        self.add_field(Form.TimeField('start_time'))
        self.add_field(Form.TimeField('end_time'))
        self.add_field(Form.TextField('description', allow_empty=True))
        self.add_field(Form.SelectId('manager_id', team_leaders))
        self.add_field(Form.SelectMultipleIds(
                'vehicles', vehicles, allow_empty=True))
        self.add_field(Form.Checkbox('cook'))
        self.add_field(Form.Select('state', Workday.STATES))

    def do_validate_end_time(self, end_time, *kw):
        if end_time.time <= self.start_time.time:
             end_time.err_msg = 'Ungültige Arbeitszeiten!'
