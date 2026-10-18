# Auto-Apply

An automated job search, matching, and application tracking system powered by Gemini AI, Apify, and automated email alerts.

## Overview
Auto-Apply streamlines the career search pipeline:
- **Job Ingestion**: Aggregates job postings using Apify scrapers.
- **AI Matching & Tailoring**: Matches candidate profiles with job requirements and drafts personalized application materials using Google Gemini.
- **Application Tracking**: Tracks submitted applications, deadlines, and follow-ups.
- **Alerts & Notifications**: Delivers automated alerts and summaries via Gmail SMTP.

## Project Structure
```text
Auto-Apply/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow
├── .env.example               # Template for environment variables
├── .gitignore                 # Excludes secrets, caches, and venv
├── README.md                  # Project overview and setup guide
└── requirements.txt           # Python dependencies (to be added)
```

## Quickstart

### 1. Clone & Set Up Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Ayush2412Rao/Auto-Apply.git
cd Auto-Apply

# Set up virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and provide your credentials:
```bash
cp .env.example .env
```
Key configurations:
- `APIFY_API_TOKEN`: Your Apify API token for scraping job boards.
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `SMTP_USER` & `SMTP_PASS`: Your Gmail address and 16-character App Password.

---
*Maintained by [@Ayush2412Rao](https://github.com/Ayush2412Rao)*
