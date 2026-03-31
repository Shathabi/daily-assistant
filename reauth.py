"""Re-authenticate Google APIs"""
from integrations.email_client import EmailClient
from integrations.calendar_client import CalendarClient

print("Authenticating Gmail... (browser will open)")
email = EmailClient()
print("✓ Gmail authenticated!")

print("\nAuthenticating Calendar... (browser will open)")
cal = CalendarClient()
print("✓ Calendar authenticated!")

print("\nAll done! Your daily assistant is ready.")
