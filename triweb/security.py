from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper, Authenticated, Everyone
from pyramid.request import RequestLocalCache
from pyramid.util import Sentinel

from triweb.models.user import User


class SecurityPolicy:

    FORGET_USER = Sentinel('FORGET_USER')

    def __init__(self, secret):
        self.authtkt = AuthTktCookieHelper(secret=secret)
        self.identity_cache = RequestLocalCache(self.load_identity)
        self.acl = ACLHelper()

    def load_identity(self, request):
        authtkt_id = self.authtkt.identify(request)
        if authtkt_id is None:
            return None
        user = request.dbsession.query(User).get(authtkt_id['userid'])
        return user

    def identity(self, request):
        identity = self.identity_cache.get_or_create(request)
        return None if identity is self.FORGET_USER else identity

    def authenticated_userid(self, request):
        user = self.identity(request)
        if user is not None:
            return user.id

    def remember(self, request, userid, **kw):
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request, **kw):
        self.identity_cache.set(request, self.FORGET_USER)
        return self.authtkt.forget(request, **kw)

    def effective_principals(self, request):
        principals = [Everyone]
        user = self.identity(request)
        if user is not None:
            principals.append(Authenticated)
            principals.append('uid:' + str(user.id))
            principals.append('role:' + user.role)
        return principals

    def permits(self, request, context, permission):
        principals = self.effective_principals(request)
        return self.acl.permits(context, principals, permission)
