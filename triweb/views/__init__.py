from pyramid.httpexceptions import HTTPForbidden


class Public(object):

    def __init__(self, request):
        self.request = request
        self.dbsession = request.dbsession
        self.push_toast = self.request.session.push_toast


class Private(Public):

    def __init__(self, request):
        if request.identity is None:
            raise HTTPForbidden()
        super().__init__(request)
