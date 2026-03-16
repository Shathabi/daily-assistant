#!/usr/bin/env python3
"""
Daily Assistant - Main Orchestrator
Collects data from all sources and sends morning brief via iMessage
"""

import os
import sys
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from integrations.email_client import EmailClient
from integrations.calendar_client import CalendarClient
from integrations.linkedin_client import LinkedInClient
from integrations.jobs_client import JobsClient
from integrations.imessage_client import iMessageClient
from generators.summarizer import ClaudeSummarizer
from generators.affirmations import get_daily_affirmation

load_dotenv()


class DailyAssistant:
    def __init__(self):
        """Initialize all clients"""
        print("Initializing Daily Assistant...")

        self.email_client = None
        self.calendar_client = None
        self.linkedin_client = None
        self.jobs_client = None
        self.imessage_client = None
        self.summarizer = None

        # Initialize clients with error handling
        try:
            self.email_client = EmailClient()
            print("✓ Email client ready")
        except Exception as e:
            print(f"⚠ Email client failed: {e}")

        try:
            self.calendar_client = CalendarClient()
            print("✓ Calendar client ready")
        except Exception as e:
            print(f"⚠ Calendar client failed: {e}")

        try:
            self.linkedin_client = LinkedInClient()
            print("✓ LinkedIn client ready")
        except Exception as e:
            print(f"⚠ LinkedIn client failed: {e}")

        try:
            self.jobs_client = JobsClient()
            print("✓ Jobs client ready")
        except Exception as e:
            print(f"⚠ Jobs client failed: {e}")

        try:
            self.imessage_client = iMessageClient()
            print("✓ iMessage client ready")
        except Exception as e:
            print(f"⚠ iMessage client failed: {e}")

        try:
            self.summarizer = ClaudeSummarizer()
            print("✓ Claude summarizer ready")
        except Exception as e:
            print(f"⚠ Claude summarizer failed: {e}")

        print()

    def collect_data(self):
        """Collect data from all sources"""
        print("Collecting data...")
        data = {}

        # Email
        if self.email_client:
            try:
                data['emails'] = self.email_client.get_priority_emails(10)
                data['world_news'] = self.email_client.get_world_news(3)
                data['growth_news'] = self.email_client.get_growth_news(3)
                print(f"✓ Collected {len(data['emails'])} emails, {len(data['world_news'])} world news, {len(data['growth_news'])} growth articles")
            except Exception as e:
                print(f"⚠ Email collection failed: {e}")
                data['emails'] = []
                data['world_news'] = []
                data['growth_news'] = []

        # Calendar
        if self.calendar_client:
            try:
                data['calendar'] = self.calendar_client.get_todays_events()
                print(f"✓ Collected {len(data['calendar'])} calendar events")
            except Exception as e:
                print(f"⚠ Calendar collection failed: {e}")
                data['calendar'] = []

        # LinkedIn
        if self.linkedin_client:
            try:
                data['linkedin'] = self.linkedin_client.get_messages(5)
                print(f"✓ Collected {len(data['linkedin'])} LinkedIn messages")
            except Exception as e:
                print(f"⚠ LinkedIn collection failed: {e}")
                data['linkedin'] = []

        # Jobs
        if self.jobs_client:
            try:
                data['jobs'] = self.jobs_client.get_new_jobs()
                print(f"✓ Collected {len(data['jobs'])} job matches")
            except Exception as e:
                print(f"⚠ Jobs collection failed: {e}")
                data['jobs'] = []

        # Affirmation
        data['affirmation'] = get_daily_affirmation()
        print("✓ Generated daily affirmation")

        print()
        return data

    def create_brief(self, data):
        """Create daily brief from collected data"""
        print("Creating daily brief with Claude...")

        if not self.summarizer:
            print("⚠ Summarizer not available, creating basic brief")
            return self._create_basic_brief(data)

        try:
            brief = self.summarizer.create_daily_brief(data)
            print("✓ Brief created")
            return brief
        except Exception as e:
            print(f"⚠ Summarization failed: {e}")
            return self._create_basic_brief(data)

    def send_brief(self, brief):
        """Send brief via iMessage"""
        print("Sending brief via iMessage...")

        if not self.imessage_client:
            print("⚠ iMessage client not available")
            print("\n" + "="*50)
            print("BRIEF CONTENT:")
            print("="*50)
            print(brief)
            print("="*50)
            return False

        try:
            result = self.imessage_client.send_message(brief)

            if result['success']:
                print(f"✓ Brief sent successfully! ({result['total_sent']} message(s))")
                return True
            else:
                print(f"✗ Failed to send brief: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"✗ Error sending brief: {e}")
            return False

    def _create_basic_brief(self, data):
        """Create a basic brief without Claude summarization"""
        from datetime import datetime
        import pytz

        et = pytz.timezone('America/New_York')
        now = datetime.now(et)

        sections = [f"🌅 Good Morning, Abi! - {now.strftime('%b %d, %I:%M %p ET')}"]

        # Email
        if data.get('emails'):
            sections.append(f"\n📧 EMAIL ({len(data['emails'])} priority)")
            for email in data['emails'][:5]:
                sections.append(f"• {email.get('subject', 'No subject')}")

        # Calendar
        if data.get('calendar'):
            sections.append(f"\n📅 CALENDAR ({len(data['calendar'])} events)")
            for event in data['calendar'][:5]:
                sections.append(f"• {event['time']} - {event['title']}")

        # Jobs
        if data.get('jobs'):
            sections.append(f"\n🎯 JOBS ({len(data['jobs'])} matches)")
            for job in data['jobs'][:3]:
                sections.append(f"• {job.get('title')} @ {job.get('company')}")

        # Affirmation
        if data.get('affirmation'):
            sections.append(f"\n💪 AFFIRMATION")
            sections.append(data['affirmation'])

        sections.append("\nHave a powerful day! 🚀")

        return "\n".join(sections)

    def run(self):
        """Main execution flow"""
        print("="*60)
        print("DAILY ASSISTANT - Starting")
        print("="*60)
        print()

        # Collect data
        data = self.collect_data()

        # Create brief
        brief = self.create_brief(data)

        # Send brief
        success = self.send_brief(brief)

        print()
        print("="*60)
        if success:
            print("✓ DAILY ASSISTANT - Completed Successfully")
        else:
            print("⚠ DAILY ASSISTANT - Completed with Errors")
        print("="*60)

        return success


if __name__ == "__main__":
    assistant = DailyAssistant()
    assistant.run()
