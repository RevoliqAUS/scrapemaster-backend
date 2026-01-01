from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# CORS配置 - 允许你的前端域名访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改为你的实际域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    targetUrl: str
    dataTypes: List[str]
    description: str = ""
    email: EmailStr
    timestamp: str

# 从环境变量读取配置
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_email_notification(data: ScrapeRequest):
    """发送Email通知"""
    if not all([NOTIFICATION_EMAIL, SMTP_USER, SMTP_PASSWORD]):
        print("Email config missing")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚀 New Scraping Request: {data.email}"
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFICATION_EMAIL
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #1a1a1a;">New Scraping Request</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <p><strong>Target URL:</strong><br>
                <a href="{data.targetUrl}">{data.targetUrl}</a></p>
                
                <p><strong>Data Types:</strong><br>
                {', '.join(data.dataTypes)}</p>
                
                <p><strong>Client Email:</strong><br>
                {data.email}</p>
                
                {f'<p><strong>Additional Notes:</strong><br>{data.description}</p>' if data.description else ''}
                
                <p><strong>Submitted:</strong><br>
                {data.timestamp}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_telegram_notification(data: ScrapeRequest):
    """发送Telegram通知"""
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        print("Telegram config missing")
        return False
    
    try:
        message = f"""
🚀 *New Scraping Request*

📍 *Target URL:*
{data.targetUrl}

📊 *Data Types:*
{', '.join(data.dataTypes)}

📧 *Client Email:*
{data.email}

{'📝 *Notes:* ' + data.description if data.description else ''}

🕐 *Time:* {data.timestamp}
        """
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        return response.status_code == 200
    
    except Exception as e:
        print(f"Telegram notification failed: {e}")
        return False

@app.get("/")
async def root():
    return {
        "status": "ScrapeMaster API Running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/submit-request")
async def submit_request(data: ScrapeRequest):
    """接收表单提交"""
    try:
        # 发送通知
        email_sent = send_email_notification(data)
        telegram_sent = send_telegram_notification(data)
        
        # 记录日志
        print(f"Request from {data.email}: {data.targetUrl}")
        print(f"Email sent: {email_sent}, Telegram sent: {telegram_sent}")
        
        return {
            "success": True,
            "message": "Request received and notification sent",
            "notifications": {
                "email": email_sent,
                "telegram": telegram_sent
            }
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
