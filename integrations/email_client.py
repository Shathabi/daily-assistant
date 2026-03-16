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
        """Initialize Gmail API client"""
        self.service = self._authenticate()

        # News sender lists from .env
        self.world_news_senders = os.getenv('WORLD_NEWS_SENDERS', '').split(',')
        self.growth_senders = os.getenv('GROWTH_MARKETING_SENDERS', '').split(',')

        # Clean up sender names
        self.world_news_senders = [s.strip() for s in self.world_news_senders if s.strip()]
        self.growth_senders = [s.strip() for s in self.growth_senders if s.strip()]

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = 'config/token.pickle'
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

        return build('gmail', 'v1', credentials=creds)

    def get_priority_emails(self, max_results=10):
        """
        Get priority emails from inbox (unread, from last 24 hours)

        Returns:
            list: Email dictionaries with sender, subject, snippet
        """
        try:
            # Query for unread emails from last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            query = f'is:unread after:{yesterday}'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                email_data = self._get_email_details(msg['id'])

                # Skip news senders (they go in separate categories)
                if not self._is_news_sender(email_data['sender']):
                    emails.append(email_data)

            return emails

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def get_world_news(self, max_results=5):
        """Get emails from world news sources"""
        return self._get_emails_from_senders(
            self.world_news_senders,
            max_results
        )

    def get_growth_news(self, max_results=5):
        """Get emails from growth marketing sources"""
        return self._get_emails_from_senders(
            self.growth_senders,
            max_results
        )

    def _get_emails_from_senders(self, senders, max_results=5):
        """
        Get unread emails from specific senders

        Args:
            senders: List of sender names
            max_results: Maximum emails to return

        Returns:
            list: Email dictionaries
        """
        if not senders:
            return []

        try:
            # Build query for multiple senders
            sender_queries = ' OR '.join([f'from:{sender}' for sender in senders])
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
            query = f'is:unread ({sender_queries}) after:{yesterday}'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                emails.append(email_data)

            return emails

        except Exception as e:
            print(f"Error fetching emails from senders: {e}")
            return []

    def _get_email_details(self, msg_id):
        """
        Get full email details

        Args:
            msg_id: Gmail message ID

        Returns:
            dict: Email data
        """
        try:
            message = self.service.users().messages().get(
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

    def _is_news_sender(self, sender):
        """Check if sender is a news source"""
        sender_lower = sender.lower()

        all_news_senders = self.world_news_senders + self.growth_senders

        for news_sender in all_news_senders:
            if news_sender.lower() in sender_lower:
                return True

        return False


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
