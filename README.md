# Flight Tracker with GitHub Actions

This project automatically tracks flights to specific airports and sends email notifications when flights are detected.

## Features

- Tracks flights to airports in Israel, Iran, Iceland, and France
- Runs automatically every 10 minutes via GitHub Actions
- Sends email notifications only when flights are detected (no spam when flight count is 0)
- Includes flight details in email notifications

## Setup Instructions

### 1. Repository Setup

1. Push this code to a GitHub repository
2. Enable GitHub Actions in your repository settings

### 2. Email Configuration

You'll need to set up the following secrets in your GitHub repository:

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

- `SENDER_EMAIL`: Your email address (e.g., `your-email@gmail.com`)
- `SENDER_PASSWORD`: Your email app password (see below for Gmail setup)
- `RECIPIENT_EMAIL`: Email address to receive notifications (can be the same as sender)
- `SMTP_SERVER`: SMTP server (default: `smtp.gmail.com` for Gmail)
- `SMTP_PORT`: SMTP port (default: `587` for Gmail)

### 3. Gmail App Password Setup (if using Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account Settings → Security → App passwords
3. Generate an app password for "Mail"
4. Use this app password (not your regular password) for `SENDER_PASSWORD`

### 4. Testing

- The workflow runs every 10 minutes automatically
- You can also trigger it manually by going to Actions → Flight Tracker → Run workflow
- Check the Actions tab to see run logs and debug any issues

## Tracked Airports

Currently tracking flights to:

- **Israel**: TLV (Tel Aviv), SDV (Sde Dov), HFA (Haifa)
- **Iran**: IKA (Tehran), MHD (Mashhad), SYZ (Shiraz)
- **Iceland**: KEF (Keflavik), RKV (Reykjavik)
- **France**: CDG (Charles de Gaulle), ORY (Orly), LYS (Lyon)

To modify the tracked airports, edit the `airports` dictionary in `main.py`.

## Email Notifications

- Emails are sent **only** when flights are detected
- If no flights are found, no email is sent (prevents spam)
- Email includes:
  - Total number of flights
  - Breakdown by country
  - Details of up to 3 flights per country
  - Timestamp of the check

## Troubleshooting

1. **No emails received**: Check GitHub Actions logs for errors
2. **Authentication errors**: Verify your email credentials and app password
3. **Workflow not running**: Ensure GitHub Actions is enabled in repository settings
4. **API errors**: The FlightRadar24 API might be rate-limited or temporarily unavailable

## Local Testing

To test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SENDER_EMAIL="your-email@gmail.com"
export SENDER_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@gmail.com"

# Run the script
python main.py
```
