#!/usr/bin/env python3
"""
Test iMessage Integration
Run this to verify your setup before scheduling daily briefs
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from integrations.imessage_client import iMessageClient

def main():
    print("="*50)
    print("Daily Assistant - iMessage Test")
    print("="*50)
    print()

    # Load environment variables
    load_dotenv()

    # Check if phone number is configured
    phone = os.getenv('YOUR_PHONE_NUMBER') or os.getenv('YOUR_IMESSAGE_ID')
    if not phone:
        print("❌ Error: No phone number configured!")
        print()
        print("Please set YOUR_PHONE_NUMBER in your .env file:")
        print("  YOUR_PHONE_NUMBER=+12345678901")
        print()
        print("Or use your Apple ID:")
        print("  YOUR_IMESSAGE_ID=shathabi@gmail.com")
        return

    print(f"📱 Target: {phone}")
    print()

    # Create client
    try:
        client = iMessageClient()
    except Exception as e:
        print(f"❌ Error creating iMessage client: {e}")
        return

    # Check Messages app
    print("Checking Messages app...")
    status = client.verify_messages_app()
    print(f"  {status['message']}")
    print()

    if not status['available']:
        print("⚠️  Please open the Messages app and try again.")
        print()
        print("Steps:")
        print("  1. Open Messages app on your Mac")
        print("  2. Make sure you're signed in with your Apple ID")
        print("  3. Run this test again")
        return

    # Send test message
    print("Sending test iMessage...")
    result = client.send_test_message()
    print()

    if result['success']:
        print("✅ SUCCESS!")
        print(f"   Sent {result['total_sent']} message(s)")
        print()
        print("📱 Check your iPhone - you should receive a test message!")
        print()
        print("If you received it, your daily assistant is ready to go! 🎉")
    else:
        print("❌ FAILED to send message")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        print()
        print("Troubleshooting:")
        print("  • Make sure Messages app is open")
        print("  • Check that you're signed into iMessage")
        print("  • Verify your phone number in .env is correct")
        print("  • Try sending a manual iMessage to yourself first")

    print()
    print("="*50)

if __name__ == "__main__":
    main()
