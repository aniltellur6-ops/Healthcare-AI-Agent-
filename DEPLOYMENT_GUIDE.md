# Deployment Guide - Healthcare AI Agent

## 🎯 Local Deployment (Development)

### Option 1: Direct Run

```bash
# Navigate to project
cd healthcare-ai-agent

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

Access at: `http://localhost:8501`

### Option 2: Virtual Environment (Recommended)

```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

---

## ☁️ Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- GitHub repository (public)
- OpenAI API key (optional)

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial Healthcare AI Agent MVP"

# Push to GitHub
git push origin main
```

#### 2. Create `.streamlit/secrets.toml` (Local Only)

Create file: `.streamlit/secrets.toml`

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

**⚠️ DO NOT COMMIT THIS FILE**

Ensure `.gitignore` contains:
```
.streamlit/secrets.toml
```

#### 3. Deploy on Streamlit Cloud

1. Visit https://streamlit.io/cloud
2. Click **"New app"**
3. Connect your GitHub account
4. Select:
   - Repository: `your-username/healthcare-ai-agent`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **"Deploy"**

#### 4. Add Secrets in Cloud

After deployment:

1. Click **⋮** (menu) → **Settings**
2. Scroll to **"Secrets"**
3. Add your secrets:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

4. **Save** and app will redeploy automatically

---

## 🧪 Testing Checklist

### Local Testing
- [ ] App runs without errors: `streamlit run app.py`
- [ ] Dashboard loads
- [ ] Can add medication
- [ ] Can view medications
- [ ] Can add health log
- [ ] Can view health logs
- [ ] Chatbot responds (with or without API key)
- [ ] Database file created at `data/health.db`
- [ ] No Python errors in terminal

### Cloud Testing
- [ ] App deploys without errors
- [ ] All features work on deployed version
- [ ] Database persists data
- [ ] AI responses work (if API key added)
- [ ] No sensitive data exposed in repo

---

## 🔒 Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `.streamlit/secrets.toml` is in `.gitignore`
- [ ] No API keys in code files
- [ ] No API keys in README.md
- [ ] Repository is public (data is demo-safe)
- [ ] `.streamlit/secrets.toml` created in Streamlit Cloud, not pushed to Git

---

## 📊 Performance Tips

1. **Database Optimization**
   - App uses SQLite (suitable for <1000 users)
   - For scaling, consider PostgreSQL

2. **API Calls**
   - LangChain caches responses
   - Consider rate limiting for production

3. **Streamlit Caching**
   - Database queries are not cached (real-time updates)
   - Consider `@st.cache_data` for heavy computations

---

## 🚨 Troubleshooting

### Deployment Fails

**Error**: `ModuleNotFoundError`
- Check `requirements.txt` has all packages
- Ensure Python version 3.8+

**Error**: `AttributeError: module 'X' has no attribute 'Y'`
- Check package versions in `requirements.txt`
- May need to pin specific versions

### App Runs Slow

- Check database size: `data/health.db`
- Reduce number of logs displayed
- Enable Streamlit caching

### Secrets Not Working

- Ensure `.env` file exists locally
- Ensure `OPENAI_API_KEY` is added to Streamlit Cloud secrets
- Restart app after adding secrets

---

## 📱 Demo Script (2 Minutes)

### Part 1: Dashboard (30s)
1. Open app at deployed URL
2. Show dashboard with metrics
3. Point to medication reminders section

### Part 2: Add Medication (30s)
1. Click "Medications" tab
2. Add: Aspirin, 500mg, 14:00
3. Show medication appears in list

### Part 3: Health Log (30s)
1. Click "Health Logs"
2. Enter: "Feeling good today"
3. Add symptom: "None"
4. Show log appears in history

### Part 4: AI Chatbot (30s)
1. Click "AI Chatbot"
2. Ask: "What helps with sleep?"
3. Show response
4. Ask: "How much water should I drink?"
5. Show response

---

## 🎉 Success Indicators

✅ App is live at Streamlit Cloud URL
✅ All tabs are clickable
✅ Medications persist after refresh
✅ Health logs show in history
✅ Chatbot responds to questions
✅ No Python errors in logs

---

**Ready to Deploy!** 🚀
