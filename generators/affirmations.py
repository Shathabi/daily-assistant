"""
Daily Affirmations Generator
Provides motivational and growth-focused affirmations for each morning brief
"""

import random
from datetime import datetime

# Curated affirmations for VP/leadership growth
AFFIRMATIONS = [
    "Great leaders don't wait for opportunities—they create them. Today, you're building the future you want to see.",

    "Your unique perspective is your superpower. Trust your instincts and lead with conviction.",

    "Growth isn't comfortable, but neither is staying where you don't belong. Today, choose growth.",

    "Every 'no' brings you closer to the right 'yes'. Keep moving forward with purpose.",

    "You've navigated challenges before and emerged stronger. Today's obstacles are tomorrow's victories.",

    "Leadership is influence, and influence starts with showing up authentically. Be yourself, boldly.",

    "The best time to start was yesterday. The second best time is right now. Make today count.",

    "Your career is a marathon, not a sprint. Pace yourself, celebrate progress, and keep pushing.",

    "Comparison is the thief of joy. Focus on your own journey and unique path to success.",

    "You don't need permission to be great. Give yourself permission to aim higher today.",

    "Failure is feedback, not a verdict. Learn, adjust, and charge forward.",

    "The world needs your unique combination of skills and experiences. Don't dim your light.",

    "Today is an opportunity to become the leader you wish you'd had earlier in your career.",

    "Your network is your net worth. Invest in relationships that matter today.",

    "Small consistent actions compound into extraordinary results. Stay the course.",

    "You're not behind. You're exactly where you need to be to get where you're going.",

    "Confidence comes from taking action despite fear. Take one bold step today.",

    "Your story isn't finished. Today is another chapter in your success journey.",

    "Great careers are built on great days. Make today one you're proud of.",

    "You've earned your seat at the table. Now make your voice heard.",
]

def get_daily_affirmation():
    """Get a daily affirmation (same one all day based on date)"""
    today = datetime.now().date()
    random.seed(str(today))
    return random.choice(AFFIRMATIONS)

if __name__ == "__main__":
    print("Today's affirmation:")
    print(get_daily_affirmation())
