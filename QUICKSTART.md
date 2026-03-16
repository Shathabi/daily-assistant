# Daily Assistant - Quick Start Guide

Get your personalized morning brief delivered via iMessage at 6 AM ET every day!

## What You'll Get Each Morning 📱

```
🌅 Good Morning, Abi! - Mar 15, 6:00 AM

📧 EMAIL (12 priority)
• Interview request from Meta recruiter
• Q1 results review - respond by EOD
• 3 LinkedIn InMails about VP roles

📅 CALENDAR (4 events)
• 9:00 AM - Team standup (30 min)
• 11:00 AM - Investor pitch prep (1 hr)
• 2:00 PM - 1:1 with Sarah (30 min)

💼 LINKEDIN (5 new)
• Message from Alex Chen (Google PM)
• Connection request: VP Growth @ Stripe

📰 WORLD NEWS
• Markets rally on tech earnings (CNN)
• 5 stories shaping politics (Tangle)

📈 GROWTH MARKETING
• How to 10x conversion rate (Kyle Poyar)
• Building growth teams (Emily Kramer)

🎯 JOBS (2 new matches)
• VP Growth @ Stripe - $350K, SF
• VP Demand Gen @ Snowflake - $320K, Remote

💪 AFFIRMATION
"Great leaders create opportunities.
Make today count."

Have a powerful day! 🚀
```

## Setup (15 minutes)

### 1. Install Dependencies

```bash
cd /Users/abiravindra/daily-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Add:
- `YOUR_PHONE_NUMBER` - Your phone number (+12345678901)
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com
- `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`
- News sender lists (already configured)

### 3. Set Up Google APIs

1. Go to https://console.cloud.google.com
2. Create project → Enable Gmail API & Calendar API
3. Create OAuth 2.0 credentials
4. Download `credentials.json`
5. Place at: `/Users/abiravindra/daily-assistant/config/credentials.json`

### 4. Run Setup

```bash
python3 setup.py
```

This will:
- Authenticate with Google (Gmail + Calendar)
- Test all integrations
- Verify iMessage works

### 5. Test the System

```bash
# Test iMessage delivery
python3 test_imessage.py

# Run full daily assistant (sends brief now)
python3 daily_assistant.py
```

### 6. Enable Daily Automation

```bash
./setup_scheduler.sh
```

✅ Done! You'll receive your brief at 6:00 AM ET daily.

## FAQ

**Q: Do I need Twilio?**
A: No! Uses iMessage (completely free).

**Q: What if LinkedIn authentication fails?**
A: LinkedIn may block automated access. The assistant will skip LinkedIn and still send other data.

**Q: Can I change the time?**
A: Yes! Edit the plist file or rerun `setup_scheduler.sh` with custom time.

**Q: How do I disable daily briefs?**
A: `launchctl unload ~/Library/LaunchAgents/com.dailyassistant.morning.plist`

**Q: Where are the logs?**
A: `/Users/abiravindra/daily-assistant/logs/daily-assistant.log`

## Customization

### Change News Sources

Edit `.env`:
```bash
WORLD_NEWS_SENDERS=CNN,Tangle,Robinhood,New York Times
GROWTH_MARKETING_SENDERS=Kyle Poyar,Emily Kramer,Lenny Rachitsky
```

### Modify Brief Format

Edit `generators/summarizer.py` to customize how Claude summarizes content.

### Add More Data Sources

Create new client in `integrations/` and add to `daily_assistant.py`.

## Troubleshooting

**iMessage not sending:**
- Make sure Messages app is open
- Check phone number in .env is correct
- Try sending manual iMessage to yourself first

**Google authentication fails:**
- Delete `config/*.pickle` files and re-run setup
- Check credentials.json is valid

**Brief is empty:**
- Check logs: `tail -20 logs/daily-assistant.log`
- Verify API keys in .env
- Test each component individually

## Support

Check the full README.md for detailed documentation.

---

Built with Claude Sonnet 4.5 🤖
