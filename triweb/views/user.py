from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.user import User
from triweb.utils.form import Form
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class UserView(Private):

    @view_config(route_name='user_add', permission="administrate",
            renderer='user_edit.jinja2')
    def view_add(self):
        mappings = {}
        mappings['action'] = 'add'
        user = User()
        mappings['roles'] = User.ROLES
        form = UserForm('user_add')
        if 'form.submitted' in self.request.params:
            if self.validate(form):
                form.copy_to(user)
                self.save_user(user)
                self.push_toast(f"Der Benutzer '{user.display_name}' wurde erfolgreich hinzugefügt!",
                        title='Benutzer erstellt!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('users'))
        mappings['form'] = form
        return mappings

    @view_config(route_name='user_edit', permission='administrate',
            renderer='user_edit.jinja2')
    def view_edit(self):
        mappings = {}
        mappings['action'] = 'edit'
        user_id = self.request.matchdict['id']
        user = self.dbsession.get(User, user_id)
        if user is None:
            raise DatabaseError(f"Benutzer mit ID: '{user_id}' nicht gefunden!")
        mappings['roles'] = User.ROLES
        form = UserForm('user_edit')
        if 'form.submitted' in self.request.params:
            if self.validate(form, user):
                form.copy_to(user)
                user = self.save_user(user)
                self.push_toast(f"Benutzer '{user.display_name}' wurde erfolgreich gespeichert!",
                        title='Benutzer gespeichert!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('users'))
        else:
            form.copy_from(user)
        mappings['form'] = form
        return mappings

    def validate(self, form, user=None):
        for field in form.validate_each(self.request.params):
            if field.name == 'email':
                if user is not None and field.value == user.email:
                    continue
                if not field.is_email():
                    field.err_msg = 'Bitte gib eine gültige e-Mail Adresse ein!'
                    continue
                # Check if a user with the same e-mail already exists
                n_users = self.dbsession.query(func.count(User.id)).\
                        filter(User.email == field.value).scalar()
                if n_users > 0:
                    field.err_msg = 'Diese e-Mail Adresse ist bereits registriert!'
                    continue
            if field.name == 'password2' \
                    and field.value != form.password1.value:
                field.err_msg = 'Die Passwörter müssen übereinstimmen!'
                continue
            if user is not None and field.name.startswith('password') \
                    and len(field.value) == 0:
                field.ignore = True
                continue
            if len(field.value) == 0:
                field.err_msg = 'Dieses Feld darf nicht leer sein!'
        return form.is_valid()

    def save_user(self, user):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(user)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return user


class UserForm(Form):

    FIELDS = [
        'firstname',
        'lastname',
        'nickname',
        'email',
        'role',
        'password1',
        'password2'
    ]

    def __init__(self, name):
        super().__init__(name, self.FIELDS)

    def copy_to(self, model):
        model.firstname = self.firstname.value
        model.lastname = self.lastname.value
        model.nickname = self.nickname.value
        model.email = self.email.value
        model.role = self.role.value
        if not self.password1.ignore:
            model.set_password(self.password1.value)
