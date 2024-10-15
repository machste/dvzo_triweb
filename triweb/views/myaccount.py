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
        user = self.request.identity
        form = MyAccountForm()
        # Check if form was submitted
        if 'myaccount.submitted' in self.request.params:
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
                form.copy_to(user)
                user = self.save_user(user)
                form.reset()
                form.copy_from(user)
        else:
            form.copy_from(user)
        return dict(form=form)

    def save_user(self, user):
        nested_transaction = self.dbsession.begin_nested()
        self.dbsession.add(user)
        try:
            nested_transaction.commit()
        except SQLAlchemyError as err:
            nested_transaction.rollback()
            raise DatabaseError(str(err))
        return user


class MyAccountForm(Form):

    FIELDS = [
        'firstname',
        'lastname',
        'nickname',
        'email',
        'password1',
        'password2'
    ]

    def __init__(self):
        super().__init__('myaccount', self.FIELDS)

    def copy_from(self, model):
        self.firstname.value = model.firstname
        self.lastname.value = model.lastname
        self.nickname.value = model.nickname
        self.email.value = model.email

    def copy_to(self, model):
        model.firstname = self.firstname.value
        model.lastname = self.lastname.value
        model.nickname = self.nickname.value
        model.email = self.email.value
        if not self.password1.ignore:
            model.set_password(self.password1.value)
