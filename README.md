# 🌟 ZHEERA — ژیرا
### Kurdish Intelligent Telegram Bot

> *ژیرا* (Zheera) means **"Wisdom / Intelligence"** in Kurdish.  
> A culturally-rich, AI-powered Telegram bot built with FastAPI + python-telegram-bot v20+, deployed on **Vercel**.

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `/start` | Welcome message in Kurdish |
| `/help` | List all commands |
| `/about` | ZHEERA's backstory and personality |
| `/fact` | A random Kurdish cultural/historical fact |
| `/ping` | Check if the bot is alive |

- 💬 Keyword-aware replies in both **Kurdish (Sorani)** and **English**
- 🤖 Webhook-based (no polling) — production-ready
- ⚡ Runs serverlessly on **Vercel**
- 🔧 Auto-registers the Telegram webhook on startup

---

## 📁 Project Structure

```
zheera/
├── api/
│   └── index.py          # Vercel entry point (FastAPI app)
├── bot/
│   ├── __init__.py
│   └── handlers.py       # Commands, message handlers, personality
├── requirements.txt
├── vercel.json           # Vercel build + routing config
├── .env.example          # Environment variable template
└── README.md
```

---

## 🚀 Deploy to Vercel

### 1. Fork / Clone
```bash
git clone https://github.com/your-username/zheera.git
cd zheera
```

### 2. Set Environment Variables in Vercel Dashboard

| Variable | Value |
|----------|-------|
| `BOT_TOKEN` | `8525301353:AAH5LjWolYzJUBO3K7r4181OIHhs_UoDzXE` |
| `WEBHOOK_URL` | `https://your-app-name.vercel.app` |

### 3. Deploy
```bash
vercel --prod
```

> After deploy, the webhook is **auto-registered** on first request.  
> You can also trigger it manually: `GET https://your-app.vercel.app/set-webhook`

---

## 🏃 Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env from template
cp .env.example .env
# Edit .env: set BOT_TOKEN and WEBHOOK_URL (use ngrok for local webhook)

# 3. Run the server
uvicorn api.index:app --reload --port 8000

# 4. (Optional) Expose locally with ngrok for webhook testing
ngrok http 8000
# Then set WEBHOOK_URL=https://<ngrok-id>.ngrok.io in .env
# Visit http://localhost:8000/set-webhook to register
```

---

## 🌿 About ZHEERA's Personality

ZHEERA is modeled after a wise, warm, and culturally-proud Kurdish character:
- Speaks both **Sorani Kurdish** and **English**
- Shares **Kurdish history, culture, and proverbs**
- Greets users with authentic Kurdish phrases
- Responds playfully while remaining helpful

---

## 🔧 Tech Stack

- **FastAPI** — async HTTP framework
- **python-telegram-bot v20+** — PTB with async support
- **Uvicorn** — ASGI server
- **Vercel** — serverless deployment platform

---

## 📜 License

MIT — Free to use, modify, and share.

---

*Made with ❤️ and Kurdish pride — دروستکراوە بە خۆشی و هەستی فەرهەنگی کوردی* 🌹
