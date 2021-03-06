"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
from __future__ import print_function
from googleapiclient.discovery import build, Resource
from httplib2 import Http
from oauth2client import file, client, tools
import datetime


def setup_gcal_service(SCOPES="https://www.googleapis.com/auth/calendar.readonly",
                       credpath='data/credentials.json') -> Resource:
    # Setup the Calendar API
    store = file.Storage(credpath)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('data/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def setup_gcal_service_key(key):
    return build('calendar', 'v3', developerKey=key)


if __name__ == '__main__':

    service = setup_gcal_service()

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
