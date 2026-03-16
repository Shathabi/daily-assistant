# Daily Assistant 🌅

Your personal morning briefing delivered via SMS at 6:00 AM ET every day.

## What You Get Each Morning

📧 **Email Summary**
- Unread priority emails
- Action items requiring response
- Important threads

📅 **Calendar Overview**
- Today's meetings with times
- Upcoming events
- Schedule conflicts

💼 **LinkedIn Updates**
- New messages
- Connection requests
- Important notifications

📰 **News Brief**
- Industry news (VP Growth, tech, marketing)
- Company news and competitor updates
- Top stories relevant to your role

🎯 **Job Search Updates**
- New VP of Growth positions matching your criteria
- Updates from target companies (Google, Meta, etc.)
- Application status tracking

💪 **Daily Affirmation**
- Motivational quote to start your day
- Growth mindset reminder

## Delivery

📱 **iMessage to your iPhone at 6:00 AM ET daily**
(Sent from your Mac via Messages app - completely free!)

## Tech Stack

- **Python 3.11+** - Core application
- **Gmail API** - Email integration
- **Google Calendar API** - Calendar events
- **LinkedIn API/Scraper** - Messages and updates
- **News API / RSS** - Industry news
- **iMessage (AppleScript)** - Message delivery via Mac Messages app
- **OpenAI API** - Summarization and intelligence
- **Schedule/Cron** - Daily automation at 6 AM ET

## Setup Instructions

### 1. Install Dependencies

```bash
cd ~/daily-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `.env` file with:
```
# Google APIs
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# LinkedIn
LINKEDIN_EMAIL=shathabi@gmail.com
LINKEDIN_PASSWORD=your_password

# News
NEWS_API_KEY=your_news_api_key

# SMS
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
YOUR_PHONE_NUMBER=+1234567890  # Your phone number

# OpenAI
OPENAI_API_KEY=your_openai_key
```

### 3. Run Setup

```bash
python setup.py  # Authenticate with Google, LinkedIn, etc.
```

### 4. Test Run

```bash
python daily_assistant.py  # Generate and send morning brief
```

### 5. Enable Daily Automation

```bash
./setup_scheduler.sh  # Schedules for 6 AM ET daily
```

## Project Structure

```
daily-assistant/
├── daily_assistant.py      # Main orchestrator
├── integrations/
│   ├── email_client.py     # Gmail integration
│   ├── calendar_client.py  # Google Calendar
│   ├── linkedin_client.py  # LinkedIn messages
│   ├── news_client.py      # News aggregation
│   ├── jobs_client.py      # Job search integration
│   └── sms_client.py       # Twilio SMS
├── generators/
│   ├── summarizer.py       # AI summarization
│   ├── affirmations.py     # Daily affirmations
│   └── formatter.py        # SMS text formatting
├── config/
│   ├── .env                # API keys (gitignored)
│   └── preferences.py      # User preferences
├── setup.py                # Initial setup script
├── setup_scheduler.sh      # Cron/launchd setup
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Sample Morning Brief

```
🌅 Good Morning, Abi! - Mar 15, 6:00 AM

📧 EMAIL (12 unread)
• Interview request from Meta recruiter
• Q1 results review - respond by EOD
• 3 LinkedIn InMails about VP roles

📅 TODAY'S CALENDAR
• 9:00 AM - Team standup (30 min)
• 11:00 AM - Investor pitch prep (1 hr)
• 2:00 PM - 1:1 with Sarah (30 min)
• 4:00 PM - Growth metrics review

💼 LINKEDIN (5 new)
• Message from Alex Chen (Google PM)
• Connection request: VP Growth @ Stripe
• 2 recruiter messages

📰 NEWS
• "AI-powered growth strategies dominate 2026"
• Meta announces new ad platform
• Your company mentioned in TechCrunch

🎯 JOBS (2 new matches)
• VP Growth @ Stripe - $350K, SF
• VP Demand Gen @ Snowflake - $320K, Remote

💪 AFFIRMATION
"Great leaders don't wait for opportunities—
they create them. Today, you're building
the future you want to see."

Have a powerful day! 🚀
```

---

**Created:** March 15, 2026
**Status:** In Development
