from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import View
from triweb.models.user import User
from triweb.utils.form import Form
from triweb.utils.db import get_user_roles
from triweb.utils.toast import Toast
from triweb.errors import DatabaseError


class UserEdit(View):

    @view_config(route_name='user_edit', permission="administrate",
            renderer='user_edit.jinja2')
    def view(self):
        user_id = self.request.matchdict['user_id']
        user = self.dbsession.get(User, user_id)
        if user is None:
            raise DatabaseError(f"Benutzer mit ID: '{user_id}' nicht gefunden!")
        user_roles = get_user_roles(self.dbsession)
        form = Form('user_edit', ['firstname', 'lastname', 'nickname', 'email',
                'role', 'password1', 'password2'])
        # Check if form was submitted
        if 'form.submitted' in self.request.params:
            for field in form.validate_each(self.request.params):
                if field.name == 'email':
                    if field.value == user.email:
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
                if field.name.startswith('password') and len(field.value) == 0:
                    field.ignore = True
                    continue
                if len(field.value) == 0:
                    field.err_msg = 'Dieses Feld darf nicht leer sein!'
            # If all fields are correct, update user account data
            if form.is_valid():
                user = self.update_user(user, form)
                self.push_toast(f"Benutzer '{user.display_name}' wurde erfolgreich gespeichert!",
                        title='Benutzer gespeichert!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('users'))
        else:
            form.populate(user)
        return dict(form=form, user_roles=user_roles)

    def update_user(self, user, form):
        # Start nested transaction
        nested_transaction = self.dbsession.begin_nested()
        # Update all neccessary fields
        user.firstname = form.firstname.value
        user.lastname = form.lastname.value
        user.nickname = form.nickname.value
        user.email = form.email.value
        user.role = form.role.value
        if len(form.password1.value) > 0:
            user.set_password(form.password1.value)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return user
