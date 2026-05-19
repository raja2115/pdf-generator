# ⚡ ReportAI — AI Engineering Report Generator

> Generate complete, professional 17-section engineering project reports as PDF in seconds using Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-green?style=flat-square&logo=flask)
![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Pro-purple?style=flat-square&logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## ✨ Features

- 🤖 **Gemini AI-Powered** — Google Gemini 2.5 Pro writes technically accurate engineering content
- 📄 **17-Section Report** — Cover, Certificate, Abstract, Components, Flowchart, Results, References & more
- 🖼️ **Real Hardware Images** — 15-25 professional photos auto-sourced from Pexels API
- 📊 **Auto Flowcharts** — System diagrams generated using Mermaid.js
- 🔄 **5-Model Fallback** — Automatic failover across 5 AI models for near-100% uptime
- ⚡ **~20 Seconds** — Full PDF generation in under 25 seconds
- 🎨 **Premium UI** — Particle canvas background, glassmorphism design, animated steps

---

## 🚀 Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/report-ai.git
cd report-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API keys
copy .env.example .env
# Edit .env and add your keys:
#   OPENROUTER_API_KEY=sk-or-...
#   PEXELS_API_KEY=...

# 5. Run
python app.py

# 6. Open browser at http://localhost:5000
```

---

## 🔑 API Keys Required

| Key | Where to Get | Cost |
|---|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) | ~$0.01/report |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api/) | Free |

---

## 🌐 Deploy to Render.com (Free)

> ⚠️ **Why not Netlify?** Netlify only supports static sites & short serverless functions (10s timeout). This app requires Python, persistent filesystem, and 15-25s generation time — making **Render.com** the correct platform.

### Steps:
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Add Environment Variables in the Render dashboard:
   - `OPENROUTER_API_KEY` = your key
   - `PEXELS_API_KEY` = your key
6. Click **Deploy** — live in ~3 minutes!

---

## 📁 Project Structure

```
report-ai/
├── app.py               # Flask backend & PDF engine
├── templates/
│   └── index.html       # Premium UI template
├── static/
│   ├── style.css        # Dark glassmorphism design
│   └── script.js        # Particles, loading steps, confetti
├── report/
│   └── system_metrics.md
├── .env.example         # API key template
├── .env                 # Your keys (NEVER commit this)
├── requirements.txt     # Python dependencies
├── Procfile             # Gunicorn start command
├── runtime.txt          # Python 3.11
└── .gitignore           # Excludes .env and venv
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| AI Engine | OpenRouter → Google Gemini 2.5 Pro |
| PDF Generation | ReportLab |
| Images | Pexels REST API |
| Flowcharts | Mermaid.ink |
| Frontend | HTML5 + CSS3 + Vanilla JS |

---

## 📊 Performance

| Metric | Value |
|---|---|
| Generation Time | 15–25 seconds |
| PDF Size | 1.2 – 3.5 MB |
| Images per Report | 15–25 |
| AI Tokens per Report | ~4,800–6,800 |
| Image Tokens | 0 (Pexels REST API) |

---

*Built with ❤️ — DSA Mini Project · Kochadai*
