from pyramid.session import SignedCookieSessionFactory

from triweb.utils.toast import Toast

def SessionFactory(secret):
    BaseSession = SignedCookieSessionFactory(secret=secret)

    class Session(BaseSession):

        def push_toast(self, message, title=None, type=Toast.Type.DEFAULT):
            self.flash((message, title, type.name), 'toasts')

        def pop_toasts(self):
            toasts = []
            for toast_args in self.pop_flash('toasts'):
                toasts.append(Toast(*toast_args))
            return toasts

        def has_toasts(self):
            return len(self.peek_flash('toasts')) > 0

    return Session
