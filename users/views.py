

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from .forms import EventForm

# OAuth scopes to access Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def home_view(request):
    """Render the home page."""
    return render(request, 'users/home.html')

def signup_view(request):
    """User signup view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

def google_calendar_auth(request):
    """Authorize the app with Google and fetch user credentials."""
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_1072312678326-ruq0sjhe8f528svihrpglb56lhv8mmko.apps.googleusercontent.com.json', SCOPES  # Ensure client_secret.json is in your project root
    )

    # Run the local server to get credentials (without passing redirect_uri explicitly)
    creds = flow.run_local_server(port=5000)

    # Store the credentials in the session for later use
    request.session['credentials'] = creds_to_dict(creds)
    return redirect('dashboard')  # Redirect to the dashboard after successful authorization




def creds_to_dict(creds):
    """Convert Google OAuth credentials to a dictionary."""
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

def fetch_upcoming_events(credentials):
    """Fetch the next 10 upcoming events from Google Calendar."""
    service = build('calendar', 'v3', credentials=credentials)

    now = datetime.utcnow().isoformat() + 'Z'  # UTC time with 'Z'
    print(f'Fetching upcoming events from {now}')

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return []

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event['summary']}")

    return events


def create_event(credentials, summary, start_time, end_time):
    """Create a new event in Google Calendar."""
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event_result['htmlLink']}")

def update_event(credentials, event_id, updated_summary):
    """Update the summary of an existing event."""
    service = build('calendar', 'v3', credentials=credentials)

    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['summary'] = updated_summary  # Modify the summary

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print(f"Event updated: {updated_event['htmlLink']}")

def delete_event(credentials, event_id):
    """Delete an event from Google Calendar."""
    service = build('calendar', 'v3', credentials=credentials)

    service.events().delete(calendarId='primary', eventId=event_id).execute()
    print(f"Event {event_id} deleted.")

def list_calendars(credentials):
    """List all calendars associated with the user's account."""
    service = build('calendar', 'v3', credentials=credentials)

    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])

    if not calendars:
        print("No calendars found.")
        return []

    for calendar in calendars:
        print(f"Calendar: {calendar['summary']} - ID: {calendar['id']}")

    return calendars


def dashboard_view(request):
    """Render the dashboard with events if authenticated."""
    if request.user.is_authenticated:
        # Check if Google Calendar credentials exist
        if 'credentials' not in request.session:
            return redirect('google_calendar_auth')  # Redirect to Google authentication

        # Load credentials from session and fetch events
        credentials = Credentials(**request.session['credentials'])
        events = fetch_upcoming_events(credentials)
        if request.method == 'POST':
            form = EventForm(request.POST)
            if form.is_valid():
                summary = form.cleaned_data['summary']
                start_time = form.cleaned_data['start_time'].isoformat() + 'Z'
                end_time = form.cleaned_data['end_time'].isoformat() + 'Z'
                create_event(credentials, summary, start_time, end_time)
                return redirect('dashboard')  # Redirect after creating the event
        else:
            form = EventForm()
        return render(request, 'users/dashboard.html', {'events': events})
    else:
        return redirect('login')

def login_view(request):
    """User login view."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
def logout_view(request):
    """Logout the user."""
    logout(request)
    return redirect('login')  # Redirect to login page after logging out
