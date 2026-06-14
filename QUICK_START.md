# 🚀 Healthcare AI Agent - Quick Start Guide

## ⚡ 5-Minute Local Setup

### Step 1: Open Terminal/Command Prompt
```bash
cd e:\Trail\healthcare-ai-agent
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
streamlit run app.py
```

**That's it!** The app opens automatically at `http://localhost:8501`

---

## 🎮 First Test (2 Minutes)

### Test 1: Add Medication
1. Go to **Medications** tab
2. Enter:
   - Name: `Aspirin`
   - Dosage: `500mg`
   - Time: `14:00`
3. Click "Add Medication"
4. ✅ Should see it in the list

### Test 2: Add Health Log
1. Go to **Health Logs** tab
2. Enter: `Feeling great today!`
3. Select symptom: `None`
4. Click "Log Entry"
5. ✅ Should see it in history

### Test 3: Chat with AI
1. Go to **AI Chatbot** tab
2. Ask: `How can I improve my sleep?`
3. ✅ Should get a response

---

## 🔑 Enable AI Chatbot (Optional)

### Get OpenAI API Key
1. Go to https://platform.openai.com/account/api-keys
2. Create new secret key
3. Copy it

### Add to .env File
1. Create file: `.env` in project root
2. Add this line:
```
OPENAI_API_KEY=sk-your_key_here
```
3. Save and restart Streamlit app

---

## 🌐 Deploy to Streamlit Cloud (10 Minutes)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Healthcare AI Agent MVP"
git push origin main
```

### Step 2: Deploy
1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your GitHub repo and `app.py`
4. Click Deploy

### Step 3: Add API Key (Optional)
1. Click app settings (gear icon)
2. Go to "Secrets"
3. Add:
```
OPENAI_API_KEY = sk-your_key_here
```

---

## 📁 Project Structure (What Does What)

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app (UI & logic) |
| `db/database.py` | SQLite database operations |
| `agent/health_agent.py` | AI chatbot logic |
| `utils/reminders.py` | Reminder alerts & validation |
| `requirements.txt` | Python packages needed |
| `data/health.db` | Database file (auto-created) |

---

## ✅ Features You Can Test Right Now

| Feature | Tab | How to Test |
|---------|-----|------------|
| Add medications | Medications | Enter name, dosage, time |
| View medications | Medications | See list after adding |
| Delete medications | Medications | Click delete button |
| Log health notes | Health Logs | Enter text and submit |
| View history | Health Logs | Scroll down to see logs |
| AI Q&A | AI Chatbot | Ask any health question |
| Dashboard stats | Dashboard | See counts and reminders |

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| `pip: command not found` | Install Python from python.org |
| `streamlit: command not found` | Run `pip install -r requirements.txt` |
| Database locked | Restart app with Ctrl+C then `streamlit run app.py` |
| AI not responding | Add OPENAI_API_KEY to .env file |

---

## 📝 Key Files to Know

### `app.py` - The Main App
- All UI pages
- Dashboard, Medications, Health Logs, Chatbot
- No need to edit unless customizing

### `db/database.py` - Database
- SQLite operations
- Stores medications, logs, reminders
- Auto-initializes on first run

### `agent/health_agent.py` - AI Brain
- Chatbot responses
- Works with or without OpenAI API
- Falls back to predefined answers

### `utils/reminders.py` - Alerts
- Checks if medication is due
- Validates user input
- Formats reminder messages

---

## 🎯 MVP Features (All Working)

✅ Add/view/delete medications
✅ Schedule medications with time
✅ Real-time medication reminders
✅ Health log tracking
✅ Symptom logging
✅ AI health chatbot
✅ SQLite database persistence
✅ Mobile-friendly Streamlit UI
✅ Cloud-deployable on Streamlit Cloud

---

## 📊 Demo Checklist (For Recruiter Review)

- [ ] Show dashboard with 3+ medications
- [ ] Trigger a reminder alert
- [ ] Add/delete medications
- [ ] Log health entry with symptom
- [ ] Ask AI chatbot question
- [ ] Show database is persisting (refresh page)
- [ ] Mention deployment on Streamlit Cloud

---

## 🎓 What's Included

✅ **Clean Code**: Easy to read, beginner-friendly
✅ **No External APIs**: Except optional OpenAI
✅ **Works Offline**: Falls back to predefined responses
✅ **SQLite**: Simple, no server needed
✅ **Streamlit**: Deploy in 1 click
✅ **Production Ready**: Can be deployed today

---

## 🔗 Useful Links

- Streamlit Docs: https://docs.streamlit.io
- LangChain Docs: https://python.langchain.com
- OpenAI API: https://platform.openai.com
- Streamlit Cloud: https://streamlit.io/cloud

---

## 💡 Tips

1. **Medication Time Format**: Use HH:MM (24-hour) - e.g., `14:30` for 2:30 PM
2. **Reminders**: Trigger when current time matches scheduled time
3. **Chatbot**: Works great without API key (uses fallback responses)
4. **Database**: Auto-created at `data/health.db` (don't delete!)
5. **Cloud Deploy**: Make sure to add secrets in Streamlit Cloud

---

## 🚀 Next Steps

1. **Run locally**: `streamlit run app.py`
2. **Test features**: Add meds, logs, chat
3. **Deploy**: Push to GitHub + Streamlit Cloud
4. **Share**: Use deployed URL for demo

---

**Ready to go!** 🎉

Questions? Check README.md or DEPLOYMENT_GUIDE.md
