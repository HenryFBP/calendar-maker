from __future__ import print_function
import calendar
import json
from copy import deepcopy
import datetime
import dateutil.parser
from pprint import pprint

from python_quickstart import setup_gcal_service, setup_gcal_service_key


def month_start_stop(date: datetime.datetime):
    """Given a datetime, return the two datetimes that are the beginning and ends of the month."""

    days = calendar.monthrange(date.year, date.month)  # tuple of two days

    start = deepcopy(date)
    end = deepcopy(date)

    start = start.replace(day=1)
    end = end.replace(day=days[1])

    return (start, end)

def eprint(event):
    """Print a GCal event in human-readable format."""
    return f"{event['summary']} from {'start'} to {'end'}"

def gdateformat(date: datetime):
    """Given a date, format it so that Google Cal HTTP API likes it."""
    return date.isoformat() + 'Z'
    

def events_match_day(events, day):
    """Given a list of events and a day, return a list of all events that take place during that day
        of the month."""
    es = []
    
    for event in events:

        # Turn ISO format into datetime.datetime
        eday = dateutil.parser.parse(event['start']['dateTime'][0])

        if eday.day == day:
            es.append(event)
    
    return es

if __name__ == '__main__':
    start, end = month_start_stop(datetime.datetime.now())

    settings = json.load(open('data/calendars.json', 'r'))

    # service = setup_gcal_service_key(json.load(open('data/key.json','r'))['key'])
    service = setup_gcal_service()

    events = {}

    for id in settings['allowed-calendar-ids']:
        events_result = service.events().list(calendarId=id, timeMin=gdateformat(start),
                                              timeMax=gdateformat(end),
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()

        events[id] = events_result.get('items', [])

        for i in range(start.day, end.day):
            print(f"{i}th day's events: ")
            pprint(events_match_day(events[id], i))

        
    pprint(events)

