import logging

from datetime import date
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

    def get_workdays_per_month(self, workdays, limit=3):
        months = []
        month = None
        for workday in workdays:
            create_new_month = False
            month_continued = False
            if month is None or not month.check_workday(workday):
                create_new_month = True
            elif len(month) >= limit:
                create_new_month = True
                month_continued = True
            if create_new_month:
                month = Calendar.Month(workday.date)
                month.continued = month_continued
                months.append(month)
            month.workdays.append(workday)
        return months

    @view_config(route_name='calendar', renderer='calendar.jinja2')
    def view(self):
        mappings = { 'month_titles': self.MONTH_NAMES }
        mappings['columns'] = self.columns
        mappings['get_poll_state'] = self.get_poll_state
        return mappings

    def get_poll_state(self, workday):
        for poll in workday.user_polls:
            if poll.user_id == self.request.identity.id:
                return poll.state
        return None


    class Month(object):

        def __init__(self, _date):
            # Reset the day of the month to the first day
            self.date = date(_date.year, _date.month, 1)
            self.workdays = []
            self.continued = False

        def __len__(self):
            return len(self.workdays)

        @property
        def num(self):
            return self.date.month

        def check_workday(self, workday):
            return self.date.month == workday.date.month \
                    and self.date.year == workday.date.year
