from __future__ import print_function
import datetime
import os.path
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']



def get_creds():
    """
    Retrieve and return creds to build calendar api service
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            print('refreshing creds')
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def schedule_caledar_event(summary, start, end):
    """
    schedule a calendar event
    """
    creds = get_creds()

    # Build a service object for interacting with the API.
    service = build('calendar', 'v3', credentials=creds)

    event = build_body(summary, start, end)
    # create event
    event = service.events().insert(calendarId='primary', body=event).execute()

    return event


def build_body(summary, start, end):
    """
    build event body
    """
    event = {
        'summary': summary,
        'start': {
            'dateTime': start,
            # central time zone
            'timeZone': 'America/Chicago',
            # 'timeZone': 'UTC'
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/Chicago',
            # 'timeZone': 'UTC'
        },
    }
    return event


def get_calendar_events(timeMin=datetime.datetime.utcnow().isoformat() + 'Z', timeMax=(datetime.datetime.utcnow() + timedelta(days=9)).isoformat() + 'Z'):
    """
    get calendar events from google api
    for a range of dates
    """
    
    creds = get_creds()

    # Build a service object for interacting with the API.
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(calendarId='primary', timeMin=timeMin,
                                        timeMax=timeMax, singleEvents=True,
                                        orderBy='startTime').execute()

    events = events_result.get('items', [])        
    return events