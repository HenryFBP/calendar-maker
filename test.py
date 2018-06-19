from __future__ import print_function
import calendar
import json
from copy import deepcopy
import datetime
import dateutil.parser
from pprint import pprint
import mpu
from yattag import Doc
from bs4 import BeautifulSoup
from python_quickstart import setup_gcal_service, setup_gcal_service_key

days = "Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday".split(',')

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
    # pprint(event)
    ret = f"{event['summary']} from {'start'} to {'end'}"
    # print(ret)
    return ret

def get_date_from_event(event, kind="start") -> datetime.datetime:
    """Given an event which may or may not have:
        - ['start']['dateTime']
        - ['start']['date']
        Return a datetime which represents that event.

        If you want to get the end, simply call this function
        and pass 'end' as the `kind` arg."""
    
    if 'start' in event:

        if 'dateTime' in event[kind]:
            return dateutil.parser.parse(event[kind]['dateTime'])

        if 'date' in event[kind]:
            return dateutil.parser.parse(event[kind]['date'])

    return None

def niceformat(date: datetime):
    """Given a date, return a super-friendly format.

    i.e. '4:30AM'"""
    return date.strftime('%I:%M%p')

def detailformat(date: datetime, sep='-'):
    """Given a date, return a detailed format. (not TOO detailed)

    i.e. '06-15-18'."""
    return date.strftime('%m'+sep+'%d'+sep+'%y')

def gdateformat(date: datetime):
    """Given a date, format it so that Google Cal HTTP API likes it."""
    return date.isoformat() + 'Z'

def sort_events_by_day(events: list) -> dict:
    """Given a list of events, sort them into a dictionary where:
        - The key is the event's day
        - The value is the event itself"""
    sortd = {}
    
    for event in events:
        edate = get_date_from_event(event)
        eday = edate.day
        
        if eday not in sortd: # Initialize dict[day] to empty list if key DNE
            sortd[eday] = []

        sortd[eday].append(event)

    for i in range(1, 32): # Ensure all days have a key
        if i not in sortd:
            sortd[i] = []

    return sortd
        

def events_match_day(events, day):
    """Given a list of events and a day, return a list of all events that take place during that day
        of the month."""
    es = []
    
    for event in events:

        eday = get_date_from_event(event)
        
        if eday.day == day:
            es.append(event)
    
    return es

def html_from_events(events: list) -> str:
    """Given a list of events, return HTML that represents those events in a calendar."""

    sortedes = sort_events_by_day(events)

    month = get_date_from_event(events[0])
    month = month.replace(day = 1)

    # Create a previous month, just 1 day before our current month.
    # This is for printing the days for the tiny previous-month section.
    prev_month = month_start_stop(month.replace(month=month.month-1))[1]
    
    doc, tag, text = Doc().tagtext()

    with tag('html'):

        with tag('head'):
            doc.stag('link',
                     ('rel', 'stylesheet'),
                     ('href', 'style.css'))
            
            doc.stag('link',
                     ('rel', 'stylesheet'),
                     ('href', 'reset.css'))

        with tag('body'):

            # Create the day headers: Su Mo Tu Th Fr Sa
            with tag('ol', klass='headers'):                
                for day in days:
                    with tag('li'):
                        with tag('h1'):
                            text(day)
                
            
            with tag('ol', klass='month'): # An ordered list of all days.
                
                # We start at the smallest day of the previous month that will fit in our mini-week of purgatory.
                prev_month = prev_month.replace(day = prev_month.day - (month.weekday() + 1))
                
                # This section of code offsets the calendar by the previous month's ending weekday.
                for i in range(0, month.weekday() + 1): 

                    # For printing the previous month's days
                    prev_month = prev_month.replace(day = prev_month.day + 1)

                    with tag('li', klass='prev'):
                        with tag('a'):
                            text(prev_month.day)
                
                for day in sorted(sortedes.keys()):
                    with tag('li'): # A single day.

                        with tag('a'):
                            text(day)

                        with tag('ul'): # An unordered list of all events for a specific day.

                            for event in sortedes[day]: # For all events in a day, do...

                                start = get_date_from_event(event)
                                end = get_date_from_event(event, 'end')
                                
                                with tag('li'): # A single event.

                                    with tag('p'): # The event's name.
                                        text(event['summary'])

                                    with tag('p', klass='time'): # The start and stop of the event.

                                        if 'dateTime' in event['start']:
                                            text(niceformat(start))
                                            text(' - ')
                                            text(niceformat(end))
                                        else:
                                            text("all day")
                                            
                                    if 'location' in event:                                    
                                        with tag('p', klass="location"): # The event's location.
                                            text('at ')
                                            text(event['location'].split(',')[0]) # The first thing before any commas, if there are any.
                                        

            text('potato')

    return BeautifulSoup(doc.getvalue(), 'html.parser').prettify()
    

if __name__ == '__main__':
    start, end = month_start_stop(datetime.datetime.now())

    settings = json.load(open('data/calendars.json', 'r'))

    # service = setup_gcal_service_key(json.load(open('data/key.json','r'))['key'])
    service = setup_gcal_service()

    events = []

    for id in settings['allowed-calendar-ids']:
        events_result = service.events().list(calendarId=id, timeMin=gdateformat(start),
                                              timeMax=gdateformat(end),
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()

        results = events_result.get('items', []) # Retrieve events matching a specific query

        for event in results:
            events.append(event)
        
    """        for i in range(start.day, end.day):
                matches = events_match_day(events[id], i)
                print(f"{i}th day's events: ")
                pprint([eprint(match) for match in matches])
    """
    
    # sortedes = sort_events_by_day(events)
    # pprint(sortedes)

    html = html_from_events(events)
    print(html)

    with open('data/calendar-' + detailformat(start) + '.html', 'w') as f:
        f.write(html)

    

