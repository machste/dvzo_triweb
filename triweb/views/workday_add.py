from datetime import date, time
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import View
from triweb.models.workday import Workday
from triweb.utils.form import Form
from triweb.utils.db import get_manager_display_names
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class WorkdayAdd(View):

    @view_config(route_name='workday_add', permission="manage",
            renderer='workday_add.jinja2')
    def view(self):
        managers = get_manager_display_names(self.dbsession)
        form = Form('workday_add', ['title', 'date', 'start_time', 'end_time',
                'description', 'manager_id', 'cook'])
        if 'form.submitted' in self.request.params:
            # Validate all fields
            for field in form.validate_each(self.request.params):
                if field.name == 'description':
                    continue
                if field.name == 'date':
                    if date.fromisoformat(field.value) < date.today():
                        field.err_msg = 'Datum liegt in der Vergangenheit!'
                    continue
                if field.name == 'end_time':
                    start_time = time.fromisoformat(form.start_time.value)
                    end_time = time.fromisoformat(field.value)
                    if start_time >= end_time:
                        field.err_msg = 'Ungültige Arbeitszeiten!'
                if field.name == 'cook':
                    field.value = field.value is not None
                    continue
                if len(field.value) == 0:
                    field.err_msg = 'Dieses Feld darf nicht leer sein!'
            # If all fields are correct, save new workday
            if form.is_valid():
                self.save_workday(form)
                self.push_toast('Der neue Arbeitstag wurde erfolgreich hinzugefügt!',
                        title='Arbeitstag erstellt!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('workdays'))
        else:
            # Populate form with default values
            self.populate_form(form)
        return dict(form=form, managers=managers)

    def populate_form(self, form):
        form.date.value = date.today().isoformat()
        form.start_time.value = '09:00'
        form.end_time.value = '17:00'
        form.manager_id.value = self.request.identity.id
        form.cook.value = False

    def reset_form(self, form):
        form.reset()
        self.populate_form(form)

    def save_workday(self, form):
        wd = Workday()
        wd.title = form.title.value
        wd.date = date.fromisoformat(form.date.value)
        wd.start_time = time.fromisoformat(form.start_time.value)
        wd.end_time = time.fromisoformat(form.end_time.value)
        wd.description = form.description.value
        wd.manager_id = form.manager_id.value
        wd.cook = form.cook.value
        # Start nested transaction
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(wd)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
