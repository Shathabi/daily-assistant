"""
Google Calendar Client
Fetches today's events and meeting schedule
"""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pytz
from dotenv import load_dotenv

load_dotenv()

# Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class CalendarClient:
    def __init__(self):
        """Initialize Google Calendar API client"""
        self.service = self._authenticate()
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        token_path = 'config/calendar_token.pickle'
        credentials_path = 'config/credentials.json'

        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('calendar', 'v3', credentials=creds)

    def get_todays_events(self, max_results=10):
        """
        Get today's calendar events

        Returns:
            list: Event dictionaries with time, title, duration, attendees
        """
        try:
            # Get start and end of today in user's timezone
            now = datetime.now(self.timezone)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Convert to RFC3339 format
            time_min = start_of_day.isoformat()
            time_max = end_of_day.isoformat()

            # Fetch events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            formatted_events = []

            for event in events:
                # Skip declined events
                if self._is_declined(event):
                    continue

                formatted_event = self._format_event(event)
                formatted_events.append(formatted_event)

            return formatted_events

        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def get_upcoming_events(self, days=3, max_results=5):
        """
        Get upcoming events for the next few days

        Args:
            days: Number of days to look ahead
            max_results: Maximum events to return

        Returns:
            list: Upcoming events
        """
        try:
            now = datetime.now(self.timezone)
            tomorrow = now + timedelta(days=1)
            future = now + timedelta(days=days)

            time_min = tomorrow.replace(hour=0, minute=0, second=0).isoformat()
            time_max = future.replace(hour=23, minute=59, second=59).isoformat()

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            formatted_events = []

            for event in events:
                if not self._is_declined(event):
                    formatted_events.append(self._format_event(event))

            return formatted_events

        except Exception as e:
            print(f"Error fetching upcoming events: {e}")
            return []

    def _format_event(self, event):
        """
        Format event data for display

        Args:
            event: Google Calendar event object

        Returns:
            dict: Formatted event data
        """
        # Get event title
        title = event.get('summary', 'Untitled')

        # Get start time
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))

        # Get end time
        end = event['end'].get('dateTime', event['end'].get('date'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

        # Calculate duration
        duration = end_dt - start_dt
        duration_str = self._format_duration(duration)

        # Format time
        time_str = start_dt.astimezone(self.timezone).strftime('%I:%M %p')

        # Get attendees
        attendees = event.get('attendees', [])
        attendee_count = len([a for a in attendees if not a.get('self', False)])

        # Check for conflicts (overlapping events handled separately)
        location = event.get('location', '')

        return {
            'title': title,
            'time': time_str,
            'start_datetime': start_dt,
            'end_datetime': end_dt,
            'duration': duration_str,
            'attendee_count': attendee_count,
            'location': location,
            'link': event.get('htmlLink', '')
        }

    def _format_duration(self, duration):
        """Format timedelta as human-readable string"""
        total_minutes = int(duration.total_seconds() / 60)

        if total_minutes < 60:
            return f"{total_minutes} min"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours}h"

    def _is_declined(self, event):
        """Check if user has declined the event"""
        attendees = event.get('attendees', [])
        for attendee in attendees:
            if attendee.get('self', False):
                return attendee.get('responseStatus') == 'declined'
        return False

    def detect_conflicts(self, events):
        """
        Detect overlapping events

        Args:
            events: List of formatted events

        Returns:
            list: Pairs of conflicting events
        """
        conflicts = []

        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                # Check if events overlap
                if (event1['start_datetime'] < event2['end_datetime'] and
                    event2['start_datetime'] < event1['end_datetime']):
                    conflicts.append((event1, event2))

        return conflicts


if __name__ == "__main__":
    # Test
    client = CalendarClient()

    print("Today's Calendar:")
    events = client.get_todays_events()

    if not events:
        print("  No events scheduled")
    else:
        for event in events:
            print(f"  • {event['time']} - {event['title']} ({event['duration']})")

        # Check for conflicts
        conflicts = client.detect_conflicts(events)
        if conflicts:
            print("\n⚠️  Conflicts detected:")
            for e1, e2 in conflicts:
                print(f"  • {e1['title']} overlaps with {e2['title']}")

    print("\nUpcoming (next 3 days):")
    upcoming = client.get_upcoming_events(days=3, max_results=3)
    for event in upcoming:
        date = event['start_datetime'].strftime('%a %b %d')
        print(f"  • {date} at {event['time']} - {event['title']}")
