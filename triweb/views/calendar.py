import logging

from pyramid.view import view_config

from triweb.views import Private
from triweb.utils.db import get_active_workdays

_log = logging.getLogger(__name__)


class Calendar(Private):

    NUM_COLUMNS = 6
    MONTH_NAMES = {
        1: 'JANUAR', 2: 'FEBRUAR', 3: 'MÄRZ', 4: 'APRIL', 5: 'MAI', 6: 'JUNI',
        7: 'JULI', 8: 'AUGUST', 9: 'SEPTEMBER', 10: 'OKTOBER', 11: 'NOVEMBER',
        12: 'DEZEMBER'
    }

    def __init__(self, request):
        super().__init__(request)
        # Initialise emtpy calender columns
        # Get all workdays of the active calendar
        workdays = get_active_workdays(self.dbsession)
        self.columns = []
        for month in self.get_workdays_per_month(workdays):
            months = [month]
            self.columns.append(months)
        if len(self.columns) > self.NUM_COLUMNS:
            #TODO: Combine months to fit into calendar columns
            self.columns = self.columns[:self.NUM_COLUMNS]

    def get_workdays_per_month(self, workdays):
        months = []
        month = None
        for workday in workdays:
            if month is None or month.num != workday.date.month:
                month = Calendar.Month(workday.date.month)
                months.append(month)
            month.workdays.append(workday)
        return months

    @view_config(route_name='calendar', renderer='calendar.jinja2')
    def view(self):
        mappings = { 'month_titles': self.MONTH_NAMES }
        mappings['columns'] = self.columns
        return mappings


    class Month(object):

        def __init__(self, num):
            self.num = num
            self.workdays = []
