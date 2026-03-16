"""
iMessage Client using AppleScript
Sends daily brief via iMessage to your iPhone
"""

import subprocess
import os
from dotenv import load_dotenv

load_dotenv()


class iMessageClient:
    def __init__(self):
        """Initialize iMessage client"""
        self.recipient = os.getenv('YOUR_PHONE_NUMBER') or os.getenv('YOUR_IMESSAGE_ID')

        if not self.recipient:
            raise ValueError(
                "Missing YOUR_PHONE_NUMBER or YOUR_IMESSAGE_ID in .env file.\n"
                "Use your phone number (e.g., +12345678901) or Apple ID email."
            )

    def send_message(self, message_body):
        """
        Send iMessage using AppleScript

        Args:
            message_body: Text content to send

        Returns:
            dict: Message status
        """
        try:
            # iMessage has no strict character limit, but split very long messages
            chunks = self._split_message(message_body, max_length=2000)

            messages_sent = []
            for i, chunk in enumerate(chunks):
                if len(chunks) > 1:
                    chunk = f"[{i+1}/{len(chunks)}]\n\n{chunk}"

                success = self._send_via_applescript(chunk)

                messages_sent.append({
                    'success': success,
                    'chunk': i + 1,
                    'total_chunks': len(chunks)
                })

            return {
                'success': all(m['success'] for m in messages_sent),
                'messages': messages_sent,
                'total_sent': len(messages_sent)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _send_via_applescript(self, message):
        """
        Send message using AppleScript and Messages app

        Args:
            message: Message text to send

        Returns:
            bool: Success status
        """
        # Escape quotes in message
        escaped_message = message.replace('"', '\\"').replace('\\', '\\\\')

        # AppleScript to send iMessage
        applescript = f'''
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant "{self.recipient}" of targetService
            send "{escaped_message}" to targetBuddy
        end tell
        '''

        try:
            # Execute AppleScript
            process = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )

            if process.returncode == 0:
                return True
            else:
                print(f"AppleScript error: {process.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("AppleScript command timed out")
            return False
        except Exception as e:
            print(f"Error sending iMessage: {e}")
            return False

    def _split_message(self, text, max_length=2000):
        """
        Split long messages into chunks

        Args:
            text: Full message text
            max_length: Maximum characters per message

        Returns:
            list: Message chunks
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""

        # Split by sections (marked by emoji headers)
        sections = text.split('\n\n')

        for section in sections:
            if len(current_chunk) + len(section) + 2 <= max_length:
                current_chunk += section + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = section + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def send_test_message(self):
        """Send a test message to verify setup"""
        test_message = "🌅 Daily Assistant Test\n\nYour daily brief system is set up correctly!\n\niMessage integration is working."
        return self.send_message(test_message)

    def verify_messages_app(self):
        """
        Verify that Messages app is available and configured

        Returns:
            dict: Status information
        """
        applescript = '''
        tell application "System Events"
            set messagesRunning to (name of processes) contains "Messages"
        end tell
        return messagesRunning
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )

            messages_available = result.stdout.strip() == 'true'

            return {
                'available': messages_available,
                'message': 'Messages app is ready' if messages_available else 'Messages app not running'
            }

        except Exception as e:
            return {
                'available': False,
                'message': f'Error checking Messages app: {e}'
            }


if __name__ == "__main__":
    # Test iMessage functionality
    print("Testing iMessage integration...\n")

    client = iMessageClient()

    # Check if Messages app is available
    status = client.verify_messages_app()
    print(f"Messages app status: {status['message']}\n")

    if status['available']:
        print(f"Sending test message to: {client.recipient}")
        result = client.send_test_message()

        if result['success']:
            print(f"✓ Test message sent successfully!")
            print(f"  Sent {result['total_sent']} message(s)")
            print(f"\nCheck your iPhone for the message!")
        else:
            print(f"✗ Failed to send message")
            if 'error' in result:
                print(f"  Error: {result['error']}")
    else:
        print("⚠ Messages app is not running. Please open Messages app and try again.")
