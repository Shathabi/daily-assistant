"""
LinkedIn Client
Fetches messages and notifications from LinkedIn
"""

import os
from linkedin_api import Linkedin
from dotenv import load_dotenv

load_dotenv()


class LinkedInClient:
    def __init__(self):
        """Initialize LinkedIn API client"""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')

        if not email or not password:
            raise ValueError(
                "Missing LinkedIn credentials. "
                "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file"
            )

        try:
            self.api = Linkedin(email, password)
        except Exception as e:
            print(f"Error authenticating with LinkedIn: {e}")
            print("Note: LinkedIn may require 2FA or may block automated access.")
            self.api = None

    def get_messages(self, max_messages=10):
        """
        Get recent LinkedIn messages

        Returns:
            list: Message dictionaries with sender, preview, timestamp
        """
        if not self.api:
            return []

        try:
            conversations = self.api.get_conversations()
            messages = []

            for conv in conversations[:max_messages]:
                # Get conversation details
                conv_id = conv.get('entityUrn', '').split(':')[-1]

                # Extract participant info
                participants = conv.get('participants', [])
                sender_name = "Unknown"

                for participant in participants:
                    if not participant.get('*messaging_member'):
                        mini_profile = participant.get('messaging_member', {}).get('miniProfile', {})
                        sender_name = f"{mini_profile.get('firstName', '')} {mini_profile.get('lastName', '')}".strip()
                        break

                # Get last message preview
                last_activity = conv.get('lastActivityAt', 0)
                preview = self._get_message_preview(conv)

                # Check if unread
                unread = conv.get('unread', False)

                messages.append({
                    'sender': sender_name,
                    'preview': preview,
                    'timestamp': last_activity,
                    'unread': unread,
                    'conversation_id': conv_id
                })

            # Sort by timestamp (most recent first)
            messages.sort(key=lambda x: x['timestamp'], reverse=True)

            return messages

        except Exception as e:
            print(f"Error fetching LinkedIn messages: {e}")
            return []

    def get_notifications(self, max_notifications=5):
        """
        Get recent LinkedIn notifications

        Returns:
            list: Notification dictionaries
        """
        if not self.api:
            return []

        try:
            # This is a placeholder - linkedin-api library has limited notification support
            # You may need to implement web scraping for full notification access
            return []

        except Exception as e:
            print(f"Error fetching notifications: {e}")
            return []

    def get_connection_requests(self):
        """
        Get pending connection requests

        Returns:
            list: Connection request info
        """
        if not self.api:
            return []

        try:
            invitations = self.api.get_invitations()
            requests = []

            for inv in invitations:
                from_member = inv.get('from', {}).get('com.linkedin.voyager.relationships.invitation.InvitationFromMember', {})
                mini_profile = from_member.get('miniProfile', {})

                name = f"{mini_profile.get('firstName', '')} {mini_profile.get('lastName', '')}".strip()
                headline = mini_profile.get('occupation', '')

                requests.append({
                    'name': name,
                    'headline': headline
                })

            return requests

        except Exception as e:
            print(f"Error fetching connection requests: {e}")
            return []

    def _get_message_preview(self, conversation):
        """Extract message preview from conversation"""
        # Try to get the last message
        events = conversation.get('events', [])
        if events:
            last_event = events[-1]
            event_content = last_event.get('eventContent', {})

            # Handle different message types
            if 'com.linkedin.voyager.messaging.event.MessageEvent' in event_content:
                message = event_content['com.linkedin.voyager.messaging.event.MessageEvent']
                text = message.get('attributedBody', {}).get('text', '')
                return text[:100]  # First 100 chars

        return "No preview available"


if __name__ == "__main__":
    # Test
    try:
        client = LinkedInClient()

        print("Recent LinkedIn Messages:")
        messages = client.get_messages(5)

        if not messages:
            print("  No messages found (or authentication failed)")
        else:
            for msg in messages:
                unread_marker = "🔵 " if msg['unread'] else ""
                print(f"  {unread_marker}From: {msg['sender']}")
                print(f"    {msg['preview']}")
                print()

        print("Connection Requests:")
        requests = client.get_connection_requests()
        if not requests:
            print("  No pending requests")
        else:
            for req in requests:
                print(f"  • {req['name']} - {req['headline']}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: LinkedIn's API has restrictions and may require manual authentication.")
        print("Consider using LinkedIn's official API or web scraping as alternative.")
