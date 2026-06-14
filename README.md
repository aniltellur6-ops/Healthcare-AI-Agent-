# Healthcare Monitoring AI Agent - MVP

A simple, deployable Streamlit app for medication tracking, reminders, and AI-powered health information.

## 🎯 Features

- **Medication Management**: Add, track, and schedule medications
- **Smart Reminders**: Time-based alerts for medication schedules
- **Health Logs**: Keep personal health notes and symptom tracking
- **AI Chatbot**: Ask general health questions (powered by LangChain + OpenAI)
- **SQLite Database**: Local data persistence

## 📋 Requirements

- Python 3.8+
- pip

## 🚀 Quick Start (Local)

### 1. Clone or Download Project

```bash
cd healthcare-ai-agent
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🔑 OpenAI Setup (Optional)

To enable AI chatbot:

1. Create `.env` file in project root:
```
OPENAI_API_KEY=your_api_key_here
```

2. Get API key from https://platform.openai.com/account/api-keys

**Note**: Without API key, the app uses predefined health responses.

## 📁 Project Structure

```
healthcare-ai-agent/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/
│   └── health.db          # SQLite database (auto-created)
├── db/
│   └── database.py        # Database operations
├── agent/
│   └── health_agent.py    # AI health agent logic
└── utils/
    └── reminders.py       # Reminder and validation utilities
```

## 🌐 Deploy to Streamlit Cloud

### Step 1: Prepare Repository

1. Push project to GitHub (public repo)
2. Create `.streamlit/secrets.toml` for API keys (DO NOT commit to Git):

```toml
OPENAI_API_KEY = "your_key_here"
```

### Step 2: Deploy

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Connect GitHub
4. Select repository and branch
5. Set main file path: `app.py`
6. Deploy!

### Step 3: Add Secrets in Cloud

1. Click app settings (gear icon)
2. Go to "Secrets"
3. Add your OpenAI API key:

```toml
OPENAI_API_KEY = "your_key_here"
```

## 📖 Usage Guide

### Dashboard
- View active medications and health logs
- See real-time medication reminders

### Medications
- Add medications with dosage and time
- View all active medications
- Remove medications

### Health Logs
- Record health notes and symptoms
- View health history

### AI Chatbot
- Ask general health questions
- Get information about common health topics
- Safe, non-diagnostic responses

## ⚠️ Important Disclaimer

This app is for **educational and general information purposes only**:
- ❌ Does NOT provide medical diagnosis
- ❌ Does NOT replace professional medical advice
- ✅ Always consult a healthcare provider for serious concerns

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite |
| AI | LangChain + OpenAI |

## 📝 Database Schema

### medications
- id: Integer (Primary Key)
- name: Text
- dosage: Text
- time_scheduled: Text (HH:MM format)
- created_at: Timestamp
- is_active: Integer

### health_logs
- id: Integer (Primary Key)
- user_note: Text
- symptom: Text
- logged_at: Timestamp

### reminders
- id: Integer (Primary Key)
- medication_id: Integer (Foreign Key)
- reminder_time: Text
- reminded_at: Timestamp

## 🎬 Demo Recording Checklist

- [ ] Add 3 medications with different times
- [ ] Wait for reminder alert on dashboard
- [ ] Add health log entry
- [ ] View health history
- [ ] Ask AI chatbot questions
- [ ] Show "About" page
- [ ] Delete a medication

## 🐛 Troubleshooting

**Issue**: `ModuleNotFoundError`
- **Solution**: Make sure you're in correct directory and virtual environment is activated

**Issue**: Database locked
- **Solution**: Restart Streamlit app

**Issue**: AI chatbot not responding
- **Solution**: Check if `OPENAI_API_KEY` is set correctly

## 📞 Support

For issues or questions, check:
1. Requirements are installed: `pip install -r requirements.txt`
2. Python version is 3.8+
3. Database file is writable in `data/` folder

---

**Version 1.0** | January 2026 | Ready for Deployment ✅
