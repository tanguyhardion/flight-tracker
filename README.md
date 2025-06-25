# Flight Tracker

A simple Python script that monitors flights to any airport and sends email alerts when flights are detected.

## What it does

- Monitors flights to all airports of the countries specified in `tracked_countries.txt`
- Sends Gmail notifications with flight details and FlightRadar24 links
- Only sends emails when flights are found (no spam)

## Quick Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Gmail credentials**
   - Use a Gmail account with App Password (not your regular password)
   - Set these environment variables:
     ```cmd
     set GMAIL_EMAIL=your-email@gmail.com
     set GMAIL_APP_PASSWORD=your-app-password
     set RECIPIENT_EMAIL=where-to-send-alerts@example.com
     ```

3. **Run the tracker**
   ```bash
   python main.py
   ```

## Getting Gmail App Password

1. Enable 2FA on your Gmail account
2. Go to Google Account settings → Security → App passwords
3. Generate an app password for "Mail"
4. Use this 16-character password (not your regular Gmail password)

## Tracked Airports

The script monitors flights to these countries:
- **Iraq**: Baghdad, Basra, Erbil, Sulaymaniyah, Najaf, Mosul, Kirkuk, Al Taqaddum
- **Iran**: Tehran, Mashhad, Shiraz, Isfahan, Tabriz, Ahvaz, Bandar Abbas, and more
- **Israel**: Tel Aviv, Haifa, Eilat airports
- **Syria**: Damascus, Aleppo, Latakia airports  
- **Jordan**: Amman, Aqaba airports
- **Lebanon**: Beirut, Kleiat airports

## What you'll get

When flights are detected, you'll receive an email with:
- Flight count by country
- Clickable FlightRadar24 links for each flight
- Flight details (call sign, route, etc.)
- Timestamp of detection

## Troubleshooting

**No emails received?**
- Check console for error messages
- Verify Gmail credentials are correct
- Make sure you're using App Password, not regular password

**API issues?**
- FlightRadar24 API might be temporarily unavailable
- Try running again in a few minutes

## Automation

Schedule the script to run automatically:
- **Windows**: Use Task Scheduler to run every 15-30 minutes
- **Linux/Mac**: Use cron jobs
