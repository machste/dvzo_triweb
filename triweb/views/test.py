import logging

from pyramid.view import view_config

from triweb.views import Public
from triweb.utils.form import Form

_log = logging.getLogger(__name__)


class Test(Public):

    ROLES = {
        1: 'Mitglied',
        2: 'Leiter',
        3: 'Hauptmann',
        4: 'Major',
        5: 'General',
        6: 'Administrator'
    }

    @view_config(route_name='test', renderer='test.jinja2')
    def view_add(self):
        mappings = {}
        mappings['roles'] = self.ROLES
        form = TestForm('test')
        if 'form.submitted' in self.request.params:
            form.validate(self.request.params)
        else:
            form.roles.value = [5, 1]
        mappings['form'] = form
        return mappings


class TestForm(Form):

    def __init__(self, name):
        super().__init__(name)
        self.add_field(Form.TextField('text'))
        self.add_field(Form.SelectMultiple('roles'))

    def do_validate_roles(self, field):
        roles = []
        for value in field.value:
            try:
                roles.append(int(value))
            except Exception:
                field.err_msg = f"Ungültiger Wert '{value}' in der Liste!"
        if len(roles) == 0:
            field.err_msg = f"Bitte wähle mindestens eine Funktion!"
        field.value = roles

