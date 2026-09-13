Live Link : https://edu-bridge-007.vercel.app/

# EduBridge — AI-Powered Higher-Education Platform

> End-to-End Decision, Financing, and Application Ecosystem

EduBridge is an enterprise-grade higher education platform engineered with Django 4.2, Firestore/PostgreSQL dual persistence, browser-based biometric Face ID authentication, and Anthropic Claude RAG integration.

---

## The 7 Core Modules

1. **Career — What to Study**: Standardized RIASEC Holland Code psychometric assessment matching 5+ career archetypes with salary benchmarks (USD & INR) and course roadmaps.
2. **Universities — Where to Study**: 1,000+ curated and College Scorecard institutions with side-by-side comparison matrices across rankings, fees, and acceptance rates.
3. **Admission — Can I Get In?**: ML scoring model with SHAP factor importance decomposition classifying targets into Safe, Target, and Reach tiers.
4. **Finance — Can I Afford It?**: 10-year break-even ROI engine with 3-scenario sensitivity testing, Section 80E tax optimization, and 6+ partner education lenders.
5. **Applications — How Do I Apply?**: University milestone checklists, deadline tracking, and AI Statement of Purpose (SOP) analysis with faculty alignment and passive voice detection.
6. **AI Advisor — What Should I Do Next?**: Context-aware RAG orchestrator utilizing official student visa guidelines, scholarship rules, and student profiles.
7. **Journey — Track My Progress**: 8-stage interactive roadmap tracking milestones from initial career discovery to consular visa interview and departure.

---

## Biometric Face ID Authentication

EduBridge features privacy-first, browser-based facial recognition powered by `face-api.js` (TensorFlow.js):
- **Local Landmark Extraction**: Computes 128-dimensional facial embedding vectors entirely in the browser.
- **Liveness Verification**: Live webcam challenge prevents photo/screen spoofing.
- **Euclidean Verification**: Server verifies vector distance ($\le 0.55$) for fast login.
- **Privacy Compliance**: Enrolled biometric vectors can be completely purged at any time from user settings (GDPR/DPDP compliance).

---

## Architecture & Data Strategy

```text
EduBridge Architecture
├── Presentation Layer: Tailwind CSS + Alpine.js + FontAwesome + aura.css / global.css
├── Biometric Engine: face-api.js (Local 128-D Embedding Extraction)
├── API Gateway: Django 4.2 REST Views & Role-Based Access Control (RBAC)
├── Data Provider Mesh:
│   ├── Curated Global Institutions Provider
│   └── US Department of Education College Scorecard Provider
├── AI & Analytics Services:
│   ├── Scikit-Learn Admission Scoring & SHAP Explainer
│   ├── RIASEC Psychometric Scorer
│   ├── Advanced Multi-Category ROI Engine
│   └── Context-Aware RAG Advisor (Anthropic Claude)
└── Storage Mesh: Firebase Firestore + SQLite / PostgreSQL Dual Persistence
```

---

## Quick Start (Development & Demo Mode)

EduBridge runs in **Zero-Config Demo Mode** out of the box using a built-in SQLite engine, enabling all AI tools, predictors, and assessments immediately.

### 1. Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate      # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run Database Migrations & Tests
```bash
python manage.py test core.tests
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` in your web browser.

---

## Production Deployment (Docker & CI/CD)

Deploy using the provided multi-stage `Dockerfile` and `docker-compose.yml`:
```bash
docker-compose up --build -d
```

### Environment Variables
| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django cryptographic secret | Required in Prod |
| `DEBUG` | Enable debug mode | `False` |
| `DATABASE_URL` | PostgreSQL connection string | SQLite fallback |
| `REDIS_URL` | Redis caching & queue endpoint | `redis://redis:6379/0` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | Built-in offline fallback |
| `COLLEGE_SCORECARD_API_KEY` | US Dept of Ed API Key | Curated fallback |
| `FACE_RECOGNITION_THRESHOLD`| Biometric match confidence | `0.85` |

---

## License & Compliance
Built for global higher education excellence. Adheres to GDPR/DPDP biometric privacy guidelines.
