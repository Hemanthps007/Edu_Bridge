# 🎓 StudyBridge — AI-Powered Student Engagement Ecosystem

> Navigate Your Path to Global Excellence

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd studybridge_project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
```

### 2. Firebase Setup
1. Go to https://console.firebase.google.com → create project
2. Project Settings → Service Accounts → Generate new private key
3. Save JSON as `firebase_credentials.json` in project root
4. Enable Firestore Database
5. Set `FIREBASE_PROJECT_ID` in `.env`

### 3. Anthropic Claude API
- Visit https://console.anthropic.com
- Create API key → set `ANTHROPIC_API_KEY` in `.env`

### 4. Run
```bash
python manage.py collectstatic --noinput
python manage.py runserver
```
Open http://127.0.0.1:8000

## 🤖 AI Features
- **AI Chatbot** — Claude-powered 24/7 study advisor
- **Career Navigator** — University & course recommendations
- **Admission Predictor** — ML scoring algorithm
- **ROI Calculator** — Financial modeling with Chart.js
- **Loan Estimator** — Dynamic eligibility from 6+ lenders

## 🔥 Firebase Collections
- `users` — Student profiles & gamification
- `assessments` — Career navigator results
- `loan_applications` — Multi-step loan forms
- `chat_history` — AI conversation logs

## 🌐 Demo Mode
Without Firebase credentials the app runs in **Demo Mode** with in-memory storage. All AI tools work normally — just configure Firebase for persistence.

## 📦 Stack
Django 4.2 · Firebase Firestore · Anthropic Claude · Tailwind CSS · Alpine.js · Chart.js
