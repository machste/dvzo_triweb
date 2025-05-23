from datetime import date
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

from triweb.views import Private
from triweb.models.vehicle import Vehicle
from triweb.utils import db
from triweb.utils.form import Form
from triweb.utils.jira.issue import Issue
from triweb.utils.jira.adf import Document
from triweb.utils.toast import Toast


class ProblemView(Private):


    @view_config(route_name='problem.report', renderer='problem_report.jinja2')
    def view_report(self):
        mappings = {}
        vehicle_id = self.request.params.get('vehicle_id')
        vehicle = None
        if vehicle_id is not None:
            vehicle = self.dbsession.get(Vehicle, vehicle_id)
        if vehicle is not None:
            vehicles = [vehicle]
        else:
            vehicles = db.get_vehicles(self.dbsession)
        mappings['vehicle'] = vehicle
        form = ProblemForm(vehicles)
        if 'form.submitted' in self.request.params:
            if form.validate(self.request.params):
                # Create new issue
                issue = Issue()
                issue.type = Issue.Type.LACK
                issue.engine = vehicle
                issue.summary = form.title.value
                doc = Document()
                doc.add_content(Document.Heading(1, 'Ausgangslage'))
                p = Document.Paragraph()
                p.add_content(Document.Text('Dieser Mangel wurde am '))
                p.add_content(Document.Date(form.date.value))
                dname = self.request.identity.display_name
                p.add_content(Document.Text(f' festgestellt und von {dname} gemeldet.'))
                doc.add_content(p)
                if len(form.description.value) != 0:
                    doc.add_content(Document.Heading(2, 'Beschreibung des Mangels'))
                    doc.add_content(Document.Paragraph(form.description.value))
                else:
                    doc.add_content('Der Mangel wurde nicht weiter beschrieben.')
                issue.description = doc
                # Send issue to jira
                self.request.jira.create_issue(issue)
                self.push_toast(f"Der Mangel für das Fahrzeug '{ vehicle.display_name }' wurde erfolgreich gemeldet!",
                        title='Mangel gemeldet!', type=Toast.Type.SUCCESS)
                return HTTPSeeOther(self.request.route_url('overview'))
        else:
            form.date.value = date.today()
        mappings['form'] = form
        return mappings


class ProblemForm(Form):

    def __init__(self, vehicles):
        super().__init__(f'problem_report')
        self.add_field(Form.SelectId('vehicle_id', vehicles))
        self.add_field(Form.TextField('title'))
        self.add_field(Form.DateField('date'))
        self.add_field(Form.TextField('description', allow_empty=True))
