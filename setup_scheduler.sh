#!/bin/bash

# Daily Assistant Scheduler Setup
# Configures macOS launchd to run daily at 6:00 AM Eastern Time

PLIST_FILE="$HOME/Library/LaunchAgents/com.dailyassistant.morning.plist"
SCRIPT_PATH="/Users/abiravindra/daily-assistant/daily_assistant.py"
VENV_PATH="/Users/abiravindra/daily-assistant/venv"
LOG_PATH="/Users/abiravindra/daily-assistant/logs"

echo "Setting up Daily Assistant Scheduler..."
echo

# Create logs directory
mkdir -p "$LOG_PATH"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "⚠  Virtual environment not found at: $VENV_PATH"
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install -r /Users/abiravindra/daily-assistant/requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
    echo
fi

# Create the launchd plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dailyassistant.morning</string>

    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PATH/bin/python3</string>
        <string>$SCRIPT_PATH</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$LOG_PATH/daily-assistant.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_PATH/daily-assistant-error.log</string>

    <key>WorkingDirectory</key>
    <string>/Users/abiravindra/daily-assistant</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>TZ</key>
        <string>America/New_York</string>
    </dict>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✓ Created launchd plist at: $PLIST_FILE"
echo

# Unload existing job if present
launchctl unload "$PLIST_FILE" 2>/dev/null

# Load the launchd job
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Daily Assistant scheduler loaded successfully!"
    echo
    echo "=================================================="
    echo "DAILY ASSISTANT - SCHEDULER ACTIVE"
    echo "=================================================="
    echo
    echo "Your morning brief will be sent at:"
    echo "  📱 6:00 AM Eastern Time (ET) daily"
    echo
    echo "Delivery method:"
    echo "  iMessage to your iPhone"
    echo
    echo "Logs:"
    echo "  Output: $LOG_PATH/daily-assistant.log"
    echo "  Errors: $LOG_PATH/daily-assistant-error.log"
    echo
    echo "Commands:"
    echo "  Test now:    python3 $SCRIPT_PATH"
    echo "  View logs:   tail -20 $LOG_PATH/daily-assistant.log"
    echo "  Check status: launchctl list | grep dailyassistant"
    echo "  Disable:     launchctl unload $PLIST_FILE"
    echo "  Re-enable:   launchctl load $PLIST_FILE"
    echo
    echo "=================================================="
else
    echo "✗ Failed to load scheduler"
    echo "Check for errors and try again"
fi
