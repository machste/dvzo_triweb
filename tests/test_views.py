from triweb import models
from triweb.views.workdays import Collect
from triweb.views.errors import notfound_view


def test_notfound_view(app_request):
    info = notfound_view(app_request)
    assert app_request.response.status_int == 404
    assert info == {}
