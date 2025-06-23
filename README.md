# Flight Tracker with Email Notifications

This project automatically tracks flights to specific airports and sends email notifications with clickable FlightRadar24 links when flights are detected.

## Features

- Tracks flights to airports anywhere in the world
- Sends email notifications only when flights are detected (no spam when flight count is 0)
- Includes flight details with clickable FlightRadar24 links in email notifications
- Shows both flight call sign and ID for easy identification
- Runs locally or can be scheduled with task schedulers

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Outlook Email Setup

You'll need to set up environment variables for email notifications:

**Required Environment Variables:**
- `OUTLOOK_EMAIL`: Your Outlook/Hotmail email address
- `OUTLOOK_PASSWORD`: Your Outlook password
- `RECIPIENT_EMAIL`: Email address to receive notifications

### 3. Setting Environment Variables

**Option A: Command Prompt (Windows)**
```cmd
set OUTLOOK_EMAIL=your-email@outlook.com
set OUTLOOK_PASSWORD=your-password
set RECIPIENT_EMAIL=recipient@example.com
python main.py
```

**Option B: PowerShell (Windows)**
```powershell
$env:OUTLOOK_EMAIL="your-email@outlook.com"
$env:OUTLOOK_PASSWORD="your-password"
$env:RECIPIENT_EMAIL="recipient@example.com"
python main.py
```

**Option C: System Environment Variables (Permanent)**
1. Press Win + R, type "sysdm.cpl" and press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "User variables", click "New" and add each variable
4. Restart your command prompt/PowerShell

**Option D: .env file (Optional)**
Create a `.env` file in the project directory:
```
OUTLOOK_EMAIL=your-email@outlook.com
OUTLOOK_PASSWORD=your-password
RECIPIENT_EMAIL=recipient@example.com
```

Then install python-dotenv: `pip install python-dotenv`
And add to main.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 4. Running the Flight Tracker

```bash
python main.py
```

## Email Notifications

- Emails are sent **only** when flights are detected
- If no flights are found, no email is sent (prevents spam)
- Email includes:
  - Total number of flights detected
  - Breakdown by country
  - **Clickable FlightRadar24 links** for each flight
  - Flight call signs and IDs
  - Route information (origin → destination)
  - Timestamp of the check

## Security Notes

- Never share your email password or commit it to version control
- Consider using App Passwords if you have 2FA enabled on Outlook
- Test with a simple email first to ensure your credentials work

## Troubleshooting

1. **No emails received**: 
   - Check console output for error messages
   - Verify environment variables are set correctly
   - Ensure your Outlook credentials are correct

2. **Authentication errors**: 
   - Verify your Outlook username and password
   - Check if you need App Passwords for 2FA accounts
   - Ensure your Outlook account allows SMTP access

3. **Connection errors**: 
   - Check your internet connection
   - Verify firewall settings allow SMTP connections
   - Try running the script manually to see detailed error messages

4. **API errors**: The FlightRadar24 API might be rate-limited or temporarily unavailable

## Local Testing

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (choose one method above)
set OUTLOOK_EMAIL=your-email@outlook.com
set OUTLOOK_PASSWORD=your-password
set RECIPIENT_EMAIL=recipient@example.com

# Run the script
python main.py
```

## Automation Options

You can automate this script using:

- **Windows Task Scheduler**: Schedule to run every 10-30 minutes
- **Cron (Linux/Mac)**: Add to crontab for regular execution
- **GitHub Actions**: Set up workflow for cloud execution (requires additional setup)

## Supported Email Providers

Currently configured for **Outlook/Hotmail** SMTP. Can be easily modified for:
- Gmail (smtp.gmail.com:587)
- Yahoo (smtp.mail.yahoo.com:587)
- Other SMTP providers
