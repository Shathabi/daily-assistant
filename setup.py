#!/usr/bin/env python3
"""
Daily Assistant Setup Script
Authenticates with Google APIs and configures the system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def setup_google_credentials():
    """Guide user through Google API setup"""
    print("="*60)
    print("GOOGLE API SETUP")
    print("="*60)
    print()
    print("To use Gmail and Calendar, you need Google API credentials.")
    print()
    print("Steps:")
    print("1. Go to: https://console.cloud.google.com")
    print("2. Create a new project (or select existing)")
    print("3. Enable Gmail API and Google Calendar API")
    print("4. Create OAuth 2.0 credentials")
    print("5. Download credentials.json")
    print("6. Place it at: /Users/abiravindra/daily-assistant/config/credentials.json")
    print()

    creds_path = 'config/credentials.json'
    if os.path.exists(creds_path):
        print("✓ credentials.json found!")
        return True
    else:
        print("⚠ credentials.json not found at:", creds_path)
        print()
        return False

def test_email():
    """Test email client"""
    print("\n" + "="*60)
    print("TESTING EMAIL CLIENT")
    print("="*60)
    print()

    try:
        from integrations.email_client import EmailClient
        client = EmailClient()
        print("✓ Email client authenticated successfully")

        # Try to fetch emails
        emails = client.get_priority_emails(3)
        print(f"✓ Found {len(emails)} priority emails")

        return True
    except Exception as e:
        print(f"✗ Email client error: {e}")
        return False

def test_calendar():
    """Test calendar client"""
    print("\n" + "="*60)
    print("TESTING CALENDAR CLIENT")
    print("="*60)
    print()

    try:
        from integrations.calendar_client import CalendarClient
        client = CalendarClient()
        print("✓ Calendar client authenticated successfully")

        events = client.get_todays_events()
        print(f"✓ Found {len(events)} events today")

        return True
    except Exception as e:
        print(f"✗ Calendar client error: {e}")
        return False

def test_imessage():
    """Test iMessage"""
    print("\n" + "="*60)
    print("TESTING iMESSAGE")
    print("="*60)
    print()

    try:
        from integrations.imessage_client import iMessageClient
        client = iMessageClient()

        status = client.verify_messages_app()
        print(f"  {status['message']}")

        if status['available']:
            print("\n✓ iMessage is ready")
            return True
        else:
            print("\n⚠ Please open Messages app")
            return False

    except Exception as e:
        print(f"✗ iMessage error: {e}")
        return False

def main():
    print()
    print("="*60)
    print("DAILY ASSISTANT SETUP")
    print("="*60)
    print()

    # Create config directory
    os.makedirs('config', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Check .env
    if not os.path.exists('.env'):
        print("⚠ .env file not found")
        print("Creating from .env.example...")
        if os.path.exists('.env.example'):
            os.system('cp .env.example .env')
            print("✓ Created .env file")
            print("\nPlease edit .env and add your:")
            print("  - Phone number/iMessage ID")
            print("  - Claude API key")
            print("  - LinkedIn credentials")
            print("\nThen run setup again.")
            sys.exit(0)

    # Check API keys
    print("Checking configuration...")
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    phone = os.getenv('YOUR_PHONE_NUMBER') or os.getenv('YOUR_IMESSAGE_ID')

    if not anthropic_key:
        print("⚠ Missing ANTHROPIC_API_KEY in .env")
    else:
        print("✓ Claude API key found")

    if not phone:
        print("⚠ Missing YOUR_PHONE_NUMBER in .env")
    else:
        print(f"✓ Phone number configured: {phone}")

    print()

    # Setup Google
    if not setup_google_credentials():
        print("\nSetup incomplete. Please add Google credentials and run again.")
        return

    # Test components
    results = {}
    results['email'] = test_email()
    results['calendar'] = test_calendar()
    results['imessage'] = test_imessage()

    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    print()

    for component, success in results.items():
        status = "✓ READY" if success else "✗ NEEDS ATTENTION"
        print(f"  {component.capitalize()}: {status}")

    if all(results.values()):
        print("\n🎉 All components ready!")
        print("\nNext steps:")
        print("  1. Test: python3 daily_assistant.py")
        print("  2. Enable daily automation: ./setup_scheduler.sh")
    else:
        print("\n⚠ Some components need attention")
        print("Fix the errors above and run setup again.")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
