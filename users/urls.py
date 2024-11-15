from django.urls import path
from .views import home_view, signup_view, dashboard_view, login_view, google_calendar_auth ,logout_view  # Added comma

urlpatterns = [
    path('', home_view, name='home'),            # Home page
    path('signup/', signup_view, name='signup'),  # Signup page
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard page
    path('login/', login_view, name='login'),     # Login page
    path('google_calendar_auth/', google_calendar_auth, name='google_calendar_auth'),  # Google Calendar Auth
    path('logout/', logout_view, name='logout'), 
]
