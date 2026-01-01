# ScrapeMaster Backend API

Professional web scraping service API.

## Features

- Accept scraping requests from frontend
- Email notifications
- Telegram notifications (optional)
- FastAPI backend

## Deployment

Deploy to Railway:
1. Connect this repository to Railway
2. Add environment variables
3. Deploy automatically

## Environment Variables

Required:
- `NOTIFICATION_EMAIL` - Your email to receive notifications
- `SMTP_USER` - Gmail address
- `SMTP_PASSWORD` - Gmail app password

Optional:
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for API documentation.
