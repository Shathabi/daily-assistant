"""
Claude-powered Summarization Engine
Uses Anthropic's Claude API to create concise, intelligent summaries
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeSummarizer:
    def __init__(self):
        """Initialize Claude API client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in .env file")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest Sonnet model

    def summarize_emails(self, emails):
        """
        Summarize a list of emails into key points

        Args:
            emails: List of email dicts with 'subject', 'sender', 'snippet'

        Returns:
            str: Concise summary
        """
        if not emails:
            return "No new emails"

        email_text = "\n\n".join([
            f"From: {e.get('sender', 'Unknown')}\nSubject: {e.get('subject', 'No subject')}\n{e.get('snippet', '')}"
            for e in emails
        ])

        prompt = f"""Analyze these emails and create a brief summary of action items and important messages.
Focus on:
- Emails requiring response or action
- Time-sensitive items
- Important updates

Emails:
{email_text}

Provide a concise summary (3-5 bullet points max) suitable for a morning text message brief."""

        return self._get_completion(prompt)

    def summarize_news(self, news_items, category="news"):
        """
        Summarize news articles

        Args:
            news_items: List of news items with 'subject' and 'snippet'
            category: Type of news (world, growth_marketing, etc.)

        Returns:
            str: Concise summary
        """
        if not news_items:
            return f"No new {category}"

        news_text = "\n\n".join([
            f"{item.get('subject', 'No subject')}\n{item.get('snippet', '')}"
            for item in news_items
        ])

        prompt = f"""Summarize these {category} articles into 2-3 key headlines.
Make it scannable for a busy executive reading on their phone.

Articles:
{news_text}

Provide 2-3 bullet points highlighting the most important or interesting items."""

        return self._get_completion(prompt)

    def summarize_linkedin_messages(self, messages):
        """
        Summarize LinkedIn messages

        Args:
            messages: List of LinkedIn message dicts

        Returns:
            str: Concise summary
        """
        if not messages:
            return "No new LinkedIn messages"

        msg_text = "\n\n".join([
            f"From: {m.get('sender', 'Unknown')}\n{m.get('preview', '')}"
            for m in messages
        ])

        prompt = f"""Summarize these LinkedIn messages. Highlight:
- Recruiter messages about job opportunities
- Networking requests from interesting people
- Messages requiring response

Messages:
{msg_text}

Provide a brief summary (2-4 bullet points) for a morning text brief."""

        return self._get_completion(prompt)

    def create_daily_brief(self, data):
        """
        Create a complete daily brief from all data sources

        Args:
            data: Dict with keys: news_emails, startup_emails, personal_emails, calendar, linkedin, jobs, affirmation

        Returns:
            str: Complete formatted brief for SMS
        """
        sections = []

        # Header
        from datetime import datetime
        import pytz
        et = pytz.timezone('America/New_York')
        now = datetime.now(et)
        header = f"🌅 Good Morning, Abi! - {now.strftime('%b %d, %I:%M %p ET')}"
        sections.append(header)

        # News Emails
        if data.get('news_emails'):
            news_count = len(data['news_emails'])
            sections.append(f"\n📰 NEWS ({news_count} new)")
            sections.append(self.summarize_news(data['news_emails'], "news"))

        # Startup Emails
        if data.get('startup_emails'):
            startup_count = len(data['startup_emails'])
            sections.append(f"\n🚀 STARTUP ({startup_count} new)")
            sections.append(self.summarize_news(data['startup_emails'], "startup insights"))

        # Personal Emails
        if data.get('personal_emails'):
            email_count = len(data['personal_emails'])
            sections.append(f"\n📧 PERSONAL ({email_count} new)")
            sections.append(self.summarize_emails(data['personal_emails']))

        # Calendar
        if data.get('calendar'):
            sections.append(f"\n📅 TODAY'S CALENDAR")
            calendar_text = self._format_calendar(data['calendar'])
            sections.append(calendar_text)

        # LinkedIn
        if data.get('linkedin'):
            msg_count = len(data['linkedin'])
            sections.append(f"\n💼 LINKEDIN ({msg_count} new)")
            sections.append(self.summarize_linkedin_messages(data['linkedin']))

        # Jobs
        if data.get('jobs'):
            job_count = len(data['jobs'])
            sections.append(f"\n🎯 JOBS ({job_count} new matches)")
            sections.append(self._format_jobs(data['jobs']))

        # Affirmation
        if data.get('affirmation'):
            sections.append(f"\n💪 AFFIRMATION")
            sections.append(data['affirmation'])

        # Footer
        sections.append("\nHave a powerful day! 🚀")

        return "\n".join(sections)

    def _format_calendar(self, events):
        """Format calendar events for SMS"""
        if not events:
            return "• No meetings scheduled"

        formatted = []
        for event in events[:5]:  # Show max 5 events
            time = event.get('time', '')
            title = event.get('title', 'Untitled')
            duration = event.get('duration', '')
            formatted.append(f"• {time} - {title} ({duration})")

        return "\n".join(formatted)

    def _format_jobs(self, jobs):
        """Format job listings for SMS"""
        if not jobs:
            return "• No new matches"

        formatted = []
        for job in jobs[:3]:  # Show max 3 jobs
            title = job.get('title', 'Untitled')
            company = job.get('company', 'Unknown')
            salary = job.get('salary', 'Not disclosed')
            location = job.get('location', '')
            formatted.append(f"• {title} @ {company} - {salary}, {location}")

        return "\n".join(formatted)

    def _get_completion(self, prompt, max_tokens=300):
        """
        Get completion from Claude

        Args:
            prompt: User prompt
            max_tokens: Maximum response length

        Returns:
            str: Claude's response
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return message.content[0].text.strip()

        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":
    # Test
    summarizer = ClaudeSummarizer()

    test_data = {
        'emails': [
            {'sender': 'recruiter@meta.com', 'subject': 'VP Growth opportunity', 'snippet': 'We have an exciting role...'},
            {'sender': 'boss@company.com', 'subject': 'Q1 Results Review', 'snippet': 'Please review by EOD...'}
        ],
        'affirmation': "Great leaders create opportunities. Make today count."
    }

    brief = summarizer.create_daily_brief(test_data)
    print(brief)
