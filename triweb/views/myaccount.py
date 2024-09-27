from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from triweb.views import Private
from triweb.models.user import User
from triweb.utils.form import Form
from triweb.errors import DatabaseError


class MyAccount(Private):

    @view_config(route_name='myaccount', renderer='myaccount.jinja2')
    def view(self):
        identity = self.request.identity
        form = Form('myaccount', ['firstname', 'lastname', 'nickname', 'email',
                'password1', 'password2'])
        # Check if form was submitted
        if 'myaccount.submitted' in self.request.params:
            for field in form.validate_each(self.request.params):
                if field.name == 'email':
                    if field.value == identity.email:
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
                user = self.update_user(form)
                form.reset()
                form.copy_from(user)
        else:
            form.copy_from(identity)
        return dict(form=form)

    def update_user(self, form):
        # Start nested transaction
        nested_transaction = self.dbsession.begin_nested()
        # Get current user from database
        user = self.dbsession.get(User, self.request.identity.id)
        # Update all neccessary fields
        user.firstname = form.firstname.value
        user.lastname = form.lastname.value
        user.nickname = form.nickname.value
        user.email = form.email.value
        if len(form.password1.value) > 0:
            user.set_password(form.password1.value)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return user
