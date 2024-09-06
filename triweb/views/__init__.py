from pyramid.httpexceptions import HTTPForbidden


class View(object):

    def __init__(self, request):
        if request.identity is None:
            raise HTTPForbidden()
        self.request = request
        self.dbsession = request.dbsession
        self.push_toast = self.request.session.push_toast
