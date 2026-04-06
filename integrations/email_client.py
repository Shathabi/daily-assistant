"""
Gmail Client
Fetches and categorizes emails for the daily brief
"""

import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailClient:
    def __init__(self):
        """Initialize Gmail API client with multiple accounts"""
        self.services = []

        # Authenticate primary account (shathabi@gmail.com)
        self.services.append(self._authenticate('config/token.pickle'))

        # Authenticate secondary account (abi.mullusoge@gmail.com)
        try:
            self.services.append(self._authenticate('config/token2.pickle'))
        except Exception as e:
            print(f"  ⚠ Second Gmail account not authenticated: {e}")

        # Email category lists from .env
        self.news_senders = os.getenv('NEWS_SENDERS', '').split(',')
        self.startup_senders = os.getenv('STARTUP_SENDERS', '').split(',')
        self.personal_senders = os.getenv('PERSONAL_SENDERS', '').split(',')

        # Clean up sender names
        self.news_senders = [s.strip() for s in self.news_senders if s.strip()]
        self.startup_senders = [s.strip() for s in self.startup_senders if s.strip()]
        self.personal_senders = [s.strip() for s in self.personal_senders if s.strip()]

    def _authenticate(self, token_path):
        """Authenticate with Gmail API"""
        creds = None
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
                # Check if running non-interactively (e.g., via launchd)
                import sys
                if not sys.stdin.isatty():
                    raise RuntimeError(
                        f"Gmail authentication required for {token_path} but running non-interactively. "
                        "Please run manually first to authenticate."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def get_personal_emails(self, max_results=10):
        """
        Get personal emails from individuals (filtering out promotional)
        Fetches from all connected Gmail accounts.
        """
        all_emails = []
        for service in self.services:
            try:
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
                query = f'is:unread after:{yesterday} -category:promotions -category:social -category:forums'

                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()

                messages = results.get('messages', [])

                for msg in messages:
                    email_data = self._get_email_details(service, msg['id'])

                    if not self._is_categorized_sender(email_data['sender']):
                        if self._is_personal_sender(email_data['sender']) or self._is_from_individual(email_data):
                            all_emails.append(email_data)

            except Exception as e:
                print(f"Error fetching personal emails: {e}")

        return all_emails[:max_results]

    def get_news_emails(self, max_results=5):
        """Get emails from news sources across all accounts"""
        return self._get_emails_from_senders(self.news_senders, max_results)

    def get_startup_emails(self, max_results=5):
        """Get emails from startup/growth sources across all accounts"""
        return self._get_emails_from_senders(self.startup_senders, max_results)

    def _get_emails_from_senders(self, senders, max_results=5):
        """
        Get unread emails from specific senders across all accounts.
        """
        if not senders:
            return []

        all_emails = []
        for service in self.services:
            try:
                sender_queries = ' OR '.join([f'from:{sender}' for sender in senders])
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
                query = f'is:unread ({sender_queries}) after:{yesterday}'

                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()

                messages = results.get('messages', [])

                for msg in messages:
                    email_data = self._get_email_details(service, msg['id'])
                    all_emails.append(email_data)

            except Exception as e:
                print(f"Error fetching emails from senders: {e}")

        return all_emails[:max_results]

    def _get_email_details(self, service, msg_id):
        """
        Get full email details from a specific service.
        """
        try:
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

            snippet = message.get('snippet', '')

            return {
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'snippet': snippet
            }

        except Exception as e:
            print(f"Error getting email details: {e}")
            return {
                'id': msg_id,
                'subject': 'Error',
                'sender': 'Unknown',
                'snippet': ''
            }

    def _is_categorized_sender(self, sender):
        """Check if sender belongs to news or startup categories"""
        sender_lower = sender.lower()

        all_category_senders = self.news_senders + self.startup_senders

        for category_sender in all_category_senders:
            if category_sender.lower() in sender_lower:
                return True

        return False

    def _is_personal_sender(self, sender):
        """Check if sender is in personal senders list"""
        sender_lower = sender.lower()

        for personal_sender in self.personal_senders:
            if personal_sender.lower() in sender_lower:
                return True

        return False

    def _is_from_individual(self, email_data):
        """
        Check if email is from an individual (not bulk/marketing)
        Uses heuristics to filter out promotional emails
        """
        sender = email_data.get('sender', '').lower()
        subject = email_data.get('subject', '').lower()

        # Filter out common promotional indicators
        promotional_keywords = [
            'noreply', 'no-reply', 'donotreply', 'newsletter', 'marketing',
            'notifications', 'automated', 'updates@', 'info@', 'hello@',
            'support@', 'team@', 'news@', 'alert', 'promo'
        ]

        # Check sender
        for keyword in promotional_keywords:
            if keyword in sender:
                return False

        # Check subject for promotional language
        promo_subject_keywords = [
            'unsubscribe', 'sale', 'discount', 'offer', 'deal',
            'limited time', 'act now', 'don\'t miss'
        ]

        for keyword in promo_subject_keywords:
            if keyword in subject:
                return False

        return True


if __name__ == "__main__":
    # Test
    client = EmailClient()

    print("Priority Emails:")
    emails = client.get_priority_emails(5)
    for email in emails:
        print(f"  - {email['subject']} (from {email['sender']})")

    print("\nWorld News:")
    world_news = client.get_world_news(3)
    for news in world_news:
        print(f"  - {news['subject']}")

    print("\nGrowth Marketing:")
    growth = client.get_growth_news(3)
    for article in growth:
        print(f"  - {article['subject']}")
