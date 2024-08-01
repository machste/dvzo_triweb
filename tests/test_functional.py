from triweb import models

def test_notfound(testapp):
    res = testapp.get('/badurl', status=404)
    assert res.status_code == 404
