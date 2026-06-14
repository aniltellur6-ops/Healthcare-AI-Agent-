# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime

# Import custom modules
from db.database import (
    init_db, add_medication, get_medications, delete_medication,
    log_health_note, get_health_logs, record_reminder,
    mark_medication_taken, is_medication_taken_today, get_today_adherence,
    log_water, get_today_water, log_mood, get_recent_moods, get_today_mood,
    export_all_data_csv,
)
from utils.reminders import (
    check_reminders, get_reminder_message, validate_medication_input,
)
from agent.health_agent import get_agent

# ── Page configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Healthcare AI Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize database ───────────────────────────────────────────────────
init_db()

# ── Session state ──────────────────────────────────────────────────────────
if "reminder_shown" not in st.session_state:
    st.session_state.reminder_shown = set()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Agent ──────────────────────────────────────────────────────────────────
agent = get_agent()

# ══════════════════════════════════════════════════════════════════════════
#  PREMIUM CSS — injected once
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Font ───────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global resets ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main App Container Background with EKG heart wave & cross grid pattern ── */
[data-testid="stAppViewContainer"] {
    background-color: #060814 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 225, 217, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(124, 58, 237, 0.08) 0px, transparent 50%),
        /* ECG Heartbeat grid pattern overlay */
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cpath d='M 10 80 H 150 M 80 10 V 150' stroke='rgba(0, 225, 217, 0.006)' stroke-width='1.5'/%3E%3C/svg%3E"),
        /* EKG pulse wave SVG background repeating */
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1000' height='400' viewBox='0 0 1000 400'%3E%3Cpath d='M 0,200 L 250,200 L 265,170 L 280,230 L 295,200 L 400,200 L 415,120 L 430,280 L 445,200 L 580,200 L 590,185 L 600,215 L 610,200 L 1000,200' fill='none' stroke='rgba(0, 225, 217, 0.016)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") !important;
    background-attachment: fixed !important;
    background-size: cover, cover, auto, 100% 400px !important;
    background-repeat: no-repeat, no-repeat, repeat, repeat-x !important;
    background-position: center center, center center, center center, center 30% !important;
}

/* ── Streamlit header override ── */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Scrollbar ─────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2d3561; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }

/* ── Sidebar ───────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090c25 0%, #050616 100%) !important;
    border-right: 1px solid rgba(0, 225, 217, 0.08);
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 10px 16px;
    border-radius: 10px;
    transition: all 0.25s ease;
    margin-bottom: 2px;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(0, 225, 217, 0.08);
}

/* ── Glass card ────────────────────────────────────────────────── */
.glass-card {
    background: rgba(17, 22, 51, 0.65);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 225, 217, 0.10);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 225, 217, 0.10);
    border-color: rgba(0, 225, 217, 0.22);
}

/* ── Stat card (dashboard metrics) ─────────────────────────────── */
.stat-card {
    background: linear-gradient(135deg, rgba(17,22,51,0.8) 0%, rgba(13,18,52,0.9) 100%);
    border: 1px solid rgba(0, 225, 217, 0.12);
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00e1d9, #7c3aed);
    border-radius: 16px 16px 0 0;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 225, 217, 0.15);
    border-color: rgba(0, 225, 217, 0.3);
}
.stat-icon { font-size: 2rem; margin-bottom: 8px; }
.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00e1d9, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.stat-label {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
    font-weight: 500;
}

/* ── Section header ────────────────────────────────────────────── */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 28px 0 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(0, 225, 217, 0.15);
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::before {
    content: "🩺";
    font-size: 1.1rem;
    filter: drop-shadow(0 0 5px rgba(0, 225, 217, 0.5));
}

/* ── Medication pill ───────────────────────────────────────────── */
.med-card {
    background: rgba(17, 22, 51, 0.55);
    border: 1px solid rgba(0, 225, 217, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
}
.med-card:hover {
    border-color: rgba(0, 225, 217, 0.2);
    background: rgba(17, 22, 51, 0.75);
}
.med-name {
    font-weight: 600;
    font-size: 1.05rem;
    color: #f1f5f9;
}
.med-dosage {
    color: #00e1d9;
    font-size: 0.9rem;
    font-weight: 500;
}
.med-time {
    color: #94a3b8;
    font-size: 0.85rem;
}

/* ── Log entry ─────────────────────────────────────────────────── */
.log-entry {
    background: rgba(17, 22, 51, 0.45);
    border-left: 3px solid #7c3aed;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.log-entry:hover {
    background: rgba(17, 22, 51, 0.65);
    border-left-color: #00e1d9;
}
.log-time {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 500;
}
.log-note {
    color: #e2e8f0;
    margin-top: 4px;
}
.log-symptom {
    display: inline-block;
    background: rgba(124, 58, 237, 0.18);
    color: #a78bfa;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.78rem;
    margin-top: 6px;
    font-weight: 500;
}

/* ── Chat bubbles ──────────────────────────────────────────────── */
div[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    border: 1px solid rgba(0, 225, 217, 0.06) !important;
    margin-bottom: 8px !important;
    backdrop-filter: blur(8px);
}

/* ── Buttons ───────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
    transition: all 0.3s ease !important;
    border: 1px solid rgba(0, 225, 217, 0.15) !important;
}
.stButton > button:hover {
    box-shadow: 0 4px 20px rgba(0, 225, 217, 0.18) !important;
    border-color: rgba(0, 225, 217, 0.35) !important;
    transform: translateY(-1px);
}

/* ── Text inputs ───────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border-radius: 10px !important;
    border: 1px solid rgba(0, 225, 217, 0.12) !important;
    transition: border-color 0.3s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00e1d9 !important;
    box-shadow: 0 0 0 2px rgba(0, 225, 217, 0.1) !important;
}

/* ── Alerts ────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 12px !important;
}

/* ── Page title ────────────────────────────────────────────────── */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 4px;
    background: linear-gradient(135deg, #00e1d9 0%, #7c3aed 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-subtitle {
    font-size: 0.95rem;
    color: #64748b;
    margin-bottom: 24px;
    font-weight: 400;
}

/* ── Badge ─────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-active {
    background: rgba(0, 225, 217, 0.12);
    color: #00e1d9;
    border: 1px solid rgba(0, 225, 217, 0.2);
}
.badge-due {
    background: rgba(251, 191, 36, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.2);
    animation: pulse-badge 2s ease-in-out infinite;
}
@keyframes pulse-badge {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── Feature cards (About page) ────────────────────────────────── */
.feature-card {
    background: linear-gradient(135deg, rgba(17,22,51,0.7) 0%, rgba(13,18,52,0.85) 100%);
    border: 1px solid rgba(0, 225, 217, 0.08);
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    transition: all 0.3s ease;
    height: 100%;
}
.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0, 225, 217, 0.12);
    border-color: rgba(0, 225, 217, 0.2);
}
.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}
.feature-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.88rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* ── Divider ───────────────────────────────────────────────────── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,225,217,0.2), rgba(124,58,237,0.2), transparent);
    margin: 24px 0;
    border: none;
}

/* ── Reminder banner ───────────────────────────────────────────── */
.reminder-banner {
    background: linear-gradient(135deg, rgba(251,191,36,0.08), rgba(251,146,60,0.08));
    border: 1px solid rgba(251, 191, 36, 0.2);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slide-in 0.4s ease;
}
@keyframes slide-in {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
}
.reminder-icon { font-size: 1.5rem; }
.reminder-text { color: #fbbf24; font-weight: 600; }
.reminder-detail { color: #94a3b8; font-size: 0.85rem; }

/* ── Disclaimer banner ─────────────────────────────────────────── */
.disclaimer {
    background: rgba(239, 68, 68, 0.06);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 12px;
    padding: 16px 20px;
    color: #fca5a5;
    font-size: 0.85rem;
    line-height: 1.6;
}

/* ── Heartbeat animation for brand logo ── */
@keyframes heart-pulse {
    0% { transform: scale(1); }
    15% { transform: scale(1.12); }
    30% { transform: scale(1); }
    45% { transform: scale(1.15); }
    60% { transform: scale(1); }
    100% { transform: scale(1); }
}
.heartbeat-logo {
    font-size: 2.8rem;
    display: inline-block;
    animation: heart-pulse 2.2s infinite ease-in-out;
    filter: drop-shadow(0 0 8px rgba(0, 225, 217, 0.3));
}

/* ── Footer ────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #475569;
    font-size: 0.8rem;
    padding: 20px 0 8px;
    border-top: 1px solid rgba(0, 225, 217, 0.06);
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)


# ── Session status summary helper for sidebar ──────────────────────────────


# ── Session status summary helper for sidebar ──────────────────────────────
def get_sidebar_stats_html():
    taken, total = get_today_adherence()
    water = get_today_water()
    mood = get_today_mood() or "Not Set"
    pct = round(taken / total * 100) if total > 0 else 0
    return f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(0,225,217,0.05); border-radius: 12px; padding: 12px; margin-top: 10px;">
        <div style="font-size: 0.8rem; font-weight: 600; color: #00e1d9; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Today's Progress</div>
        <div style="font-size: 0.85rem; margin-bottom: 6px; color: #e2e8f0;">💊 Adherence: <span style="font-weight: 700; color: #a78bfa;">{taken}/{total} ({pct}%)</span></div>
        <div style="font-size: 0.85rem; margin-bottom: 6px; color: #e2e8f0;">💧 Water: <span style="font-weight: 700; color: #3b82f6;">{water}/8 gl.</span></div>
        <div style="font-size: 0.85rem; color: #e2e8f0;">😊 Mood: <span style="font-weight: 700; color: #10b981;">{mood}</span></div>
    </div>
    """


# ══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div class="heartbeat-logo">🩺</div>
        <div style="font-size:1.2rem; font-weight:800;
                    background: linear-gradient(135deg, #00e1d9, #7c3aed);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text; margin-top:4px;">
            HealthCare AI
        </div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
            Intelligent Health Monitoring
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["Dashboard", "Medications", "Health Logs", "BMI Calculator", "AI Chatbot", "About"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Render quick stats
    st.markdown(get_sidebar_stats_html(), unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Sidebar status
    mode = "🟢 Online (OpenAI)" if agent.use_llm else "🔵 Offline (Keywords)"
    st.markdown(f"""
    <div style="text-align:center; padding: 8px 0;">
        <div style="font-size:0.78rem; color:#64748b;">Agent Status</div>
        <div style="font-size:0.85rem; color:#94a3b8; font-weight:500; margin-top:4px;">
            {mode}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your health overview at a glance</div>',
                unsafe_allow_html=True)

    medications = get_medications()
    health_logs = get_health_logs()
    due_meds = check_reminders(medications) if medications else []
    taken_count, total_count = get_today_adherence()
    water_today = get_today_water()
    mood_today = get_today_mood() or "Not Set"

    # ── Stat cards ──
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, "💊", len(medications), "Active Meds"),
        (c2, "📅", f"{taken_count}/{total_count}" if total_count > 0 else "0/0", "Adherence"),
        (c3, "💧", f"{water_today}/8", "Water Intake"),
        (c4, "😊", mood_today, "Mood Today"),
    ]
    for col, icon, value, label in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-value" style="font-size:1.8rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Adherence Progress Bar ──
    if total_count > 0:
        pct = round(taken_count / total_count * 100)
        st.markdown(f"""
        <div style="margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.95rem; font-weight:600; color:#e2e8f0;">💊 Daily Medication Adherence</span>
            <span style="font-size:0.9rem; font-weight:700; color:#00d4ff;">{pct}% completed</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(taken_count / total_count)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── Reminders & Actions ──
    st.markdown('<div class="section-header">⏰ Medication Reminders</div>',
                unsafe_allow_html=True)

    if due_meds:
        for med in due_meds:
            mid = med["id"]
            if mid not in st.session_state.reminder_shown:
                st.session_state.reminder_shown.add(mid)
                record_reminder(mid)
            
            taken = is_medication_taken_today(mid)
            
            c_med1, c_med2 = st.columns([5, 1])
            with c_med1:
                st.markdown(f"""
                <div class="reminder-banner">
                    <div class="reminder-icon">⏰</div>
                    <div>
                        <div class="reminder-text">{med['name']} — {med['dosage']}</div>
                        <div class="reminder-detail">Scheduled at {med['time_scheduled']} · Take now</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c_med2:
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                if taken:
                    st.markdown('<span class="badge badge-active" style="display:block; text-align:center; padding:8px 0;">TAKEN</span>', unsafe_allow_html=True)
                else:
                    if st.button("Mark Taken", key=f"take_due_{mid}", use_container_width=True):
                        mark_medication_taken(mid)
                        st.success(f"Taken {med['name']}!")
                        st.rerun()
    elif medications:
        st.info("✅ No medications due right now. Next reminder will appear within ±5 min of scheduled time.")
    else:
        st.info("No medications scheduled. Head to **Medications** to add your first one.")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Water Intake Tracker Section ──
    st.markdown('<div class="section-header">💧 Water Intake Tracker</div>', unsafe_allow_html=True)
    c_water1, c_water2 = st.columns([3, 1])
    with c_water1:
        water_glasses = "💧" * min(water_today, 8) + "⚪" * max(0, 8 - water_today)
        if water_today > 8:
            water_glasses += f" (+{water_today - 8} extra)"
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 20px;">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">{water_glasses}</div>
            <div style="font-size: 0.9rem; color: #94a3b8;">Goal: 8 glasses daily (approx. 2 liters)</div>
        </div>
        """, unsafe_allow_html=True)
    with c_water2:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🥛 +1", use_container_width=True, key="add_water_dash"):
                log_water(1)
                st.rerun()
        with col_btn2:
            if st.button("🗑️ -1", use_container_width=True, key="remove_water_dash"):
                log_water(-1)
                st.rerun()

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Recent logs ──
    st.markdown('<div class="section-header">📝 Recent Health Logs</div>',
                unsafe_allow_html=True)
    if health_logs:
        for log in health_logs[:5]:
            symptom_html = (
                f'<span class="log-symptom">{log["symptom"]}</span>'
                if log["symptom"] else ""
            )
            st.markdown(f"""
            <div class="log-entry">
                <div class="log-time">{log['logged_at']}</div>
                <div class="log-note">{log['user_note']}</div>
                {symptom_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No health logs yet. Start logging in **Health Logs**.")


# ══════════════════════════════════════════════════════════════════════════
#  MEDICATIONS
# ══════════════════════════════════════════════════════════════════════════
elif page == "Medications":
    st.markdown('<div class="page-title">💊 Medications</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage your medication schedule</div>',
                unsafe_allow_html=True)

    # ── Add form ──
    with st.container():
        st.markdown('<div class="section-header">➕ Add New Medication</div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            med_name = st.text_input("Name", placeholder="e.g., Aspirin",
                                     label_visibility="collapsed")
        with c2:
            med_dosage = st.text_input("Dosage", placeholder="e.g., 500 mg",
                                       label_visibility="collapsed")
        with c3:
            med_time = st.text_input("Time (HH:MM)", placeholder="e.g., 08:30",
                                     label_visibility="collapsed")

        if st.button("💊 Add Medication", use_container_width=True, type="primary"):
            is_valid, msg = validate_medication_input(med_name, med_dosage, med_time)
            if is_valid:
                add_medication(med_name.strip(), med_dosage.strip(), med_time.strip())
                st.success(f"✅ **{med_name}** added successfully!")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── List ──
    st.markdown('<div class="section-header">📋 Current Medications & Adherence</div>',
                unsafe_allow_html=True)
    medications = get_medications()

    if medications:
        for med in medications:
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
            with c1:
                st.markdown(f"""
                <div class="med-name" style="padding-top:8px;">{med['name']}</div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="med-dosage" style="padding-top:8px;">{med['dosage']}</div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="med-time" style="padding-top:8px;">🕐 {med['time_scheduled']}</div>
                """, unsafe_allow_html=True)
            with c4:
                taken = is_medication_taken_today(med['id'])
                if taken:
                    st.markdown('<span class="badge badge-active" style="display:inline-block; margin-top:8px;">✅ TAKEN TODAY</span>', unsafe_allow_html=True)
                else:
                    if st.button("Mark Taken", key=f"take_list_{med['id']}", use_container_width=True):
                        mark_medication_taken(med['id'])
                        st.success(f"Taken {med['name']}!")
                        st.rerun()
            with c5:
                if st.button("🗑️", key=f"del_{med['id']}",
                             help="Remove this medication"):
                    delete_medication(med["id"])
                    st.rerun()
            st.markdown('<div style="height:1px; background:rgba(0,212,255,0.05); margin:4px 0 8px;"></div>',
                        unsafe_allow_html=True)
    else:
        st.info("No medications yet. Add one above to get started.")


# ══════════════════════════════════════════════════════════════════════════
#  HEALTH LOGS
# ══════════════════════════════════════════════════════════════════════════
elif page == "Health Logs":
    st.markdown('<div class="page-title">📝 Health Logs</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Track your symptoms, mood and well-being</div>',
                unsafe_allow_html=True)

    # ── Mood Tracker Emojis ──
    st.markdown('<div class="section-header">😊 How is your mood today?</div>', unsafe_allow_html=True)
    mood_options = {
        "😊 Happy": "Happy",
        "😐 Neutral": "Neutral",
        "😔 Sad": "Sad",
        "😠 Angry": "Angry",
        "🤒 Sick": "Sick",
        "😴 Tired": "Tired"
    }
    cols = st.columns(6)
    for idx, (label, val) in enumerate(mood_options.items()):
        with cols[idx]:
            if st.button(label, use_container_width=True, key=f"mood_btn_{val}"):
                log_mood(val)
                st.success(f"Logged mood: {val}")
                st.rerun()

    mood_today = get_today_mood()
    if mood_today:
        st.markdown(f"<div style='text-align:center; color:#00d4ff; font-weight:600; margin-bottom:15px; font-size:0.9rem;'>Today's Mood: {mood_today}</div>", unsafe_allow_html=True)

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

    # ── Add log form ──
    st.markdown('<div class="section-header">📝 Write a Health Note</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        user_note = st.text_area("What's on your mind?",
                                 placeholder="e.g., Feeling tired after lunch…",
                                 height=100, label_visibility="collapsed")
    with c2:
        symptom = st.selectbox(
            "Symptom (optional)",
            ["None", "Headache", "Fever", "Cough", "Fatigue",
             "Nausea", "Pain", "Anxiety", "Other"],
            label_visibility="collapsed",
        )

    if st.button("📝 Log Entry", use_container_width=True, type="primary"):
        if user_note and user_note.strip():
            log_health_note(user_note.strip(),
                            symptom if symptom != "None" else "")
            st.success("✅ Log recorded!")
            st.rerun()
        else:
            st.error("Please enter a note.")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Mood History ──
    recent_moods = get_recent_moods(7)
    if recent_moods:
        st.markdown('<div class="section-header">📈 Recent Mood History (Last 7 Days)</div>', unsafe_allow_html=True)
        mood_emojis = {"Happy": "😊", "Neutral": "😐", "Sad": "😔", "Angry": "😠", "Sick": "🤒", "Tired": "😴"}
        
        # Display horizontal timeline layout
        mood_cols = st.columns(min(len(recent_moods), 7))
        for idx, m in enumerate(recent_moods[:7]):
            with mood_cols[idx]:
                emoji = mood_emojis.get(m['mood'], "✨")
                dt = datetime.strptime(m['logged_at'], "%Y-%m-%d %H:%M:%S")
                time_lbl = dt.strftime("%b %d")
                st.markdown(f"""
                <div style="text-align:center; padding:12px; background:rgba(255,255,255,0.03); border:1px solid rgba(0,212,255,0.08); border-radius:12px;">
                    <div style="font-size:1.8rem; margin-bottom:4px;">{emoji}</div>
                    <div style="font-size:0.8rem; font-weight:600; color:#e2e8f0;">{m['mood']}</div>
                    <div style="font-size:0.7rem; color:#64748b;">{time_lbl}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)

    # ── Health History ──
    st.markdown('<div class="section-header">📜 Health History</div>',
                unsafe_allow_html=True)
    logs = get_health_logs()
    if logs:
        for log in logs:
            symptom_html = (
                f'<span class="log-symptom">{log["symptom"]}</span>'
                if log["symptom"] else ""
            )
            st.markdown(f"""
            <div class="log-entry">
                <div class="log-time">{log['logged_at']}</div>
                <div class="log-note">{log['user_note']}</div>
                {symptom_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No health logs yet. Start journaling above.")

    # ── CSV Export ──
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📥 Export Data</div>', unsafe_allow_html=True)
    try:
        csv_data = export_all_data_csv()
        st.download_button(
            label="💾 Download All Health Data (CSV)",
            data=csv_data,
            file_name=f"healthcare_logs_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error preparing download: {e}")


# ══════════════════════════════════════════════════════════════════════════
#  BMI CALCULATOR (NEW)
# ══════════════════════════════════════════════════════════════════════════
elif page == "BMI Calculator":
    st.markdown('<div class="page-title">🧮 BMI Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Calculate your Body Mass Index and check health tips</div>',
                unsafe_allow_html=True)

    unit_system = st.radio("Choose Unit System", ["Metric (kg / cm)", "Imperial (lbs / inches)"], horizontal=True)

    c1, c2 = st.columns(2)
    if unit_system == "Metric (kg / cm)":
        with c1:
            weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
        with c2:
            height = st.number_input("Height (cm)", min_value=30.0, max_value=300.0, value=170.0, step=0.1)
    else:
        with c1:
            weight_lbs = st.number_input("Weight (lbs)", min_value=1.0, max_value=1100.0, value=154.0, step=0.1)
            weight = weight_lbs * 0.45359237
        with c2:
            height_in = st.number_input("Height (inches)", min_value=12.0, max_value=120.0, value=67.0, step=0.1)
            height = height_in * 2.54

    if st.button("🧮 Calculate BMI", type="primary", use_container_width=True):
        height_m = height / 100.0
        bmi = weight / (height_m * height_m)

        # Categorize
        if bmi < 18.5:
            category = "Underweight"
            color = "#3b82f6"
            advice = "It is recommended to focus on nutrient-dense foods, balanced meals, and strength training to build muscle mass safely. Consult a physician or nutritionist if needed."
        elif 18.5 <= bmi <= 24.9:
            category = "Normal Weight"
            color = "#10b981"
            advice = "Great job! Keep doing what you're doing. A balanced diet and regular physical activity are key to maintaining a healthy weight."
        elif 25.0 <= bmi <= 29.9:
            category = "Overweight"
            color = "#f59e0b"
            advice = "Consider incorporating more physical activity (at least 150 minutes of moderate activity weekly) and prioritizing whole foods like vegetables, lean proteins, and fiber."
        else:
            category = "Obese"
            color = "#ef4444"
            advice = "It is highly recommended to consult with a primary care doctor or dietitian to create a sustainable, personalized weight management plan. Focus on gradual, healthy changes."

        # Map BMI visually from 10 to 40
        marker_pct = min(max((bmi - 10) / 30 * 100, 0), 100)

        st.markdown(f"""
        <div class="glass-card" style="margin-top:20px; border-left: 5px solid {color};">
            <div style="font-size:0.85rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Your Results</div>
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin: 12px 0;">
                <span style="font-size:3.5rem; font-weight:800; color:#f1f5f9;">{bmi:.1f}</span>
                <span style="font-size:1.5rem; font-weight:700; color:{color};">{category}</span>
            </div>
            
            <!-- Color Indicator Bar -->
            <div style="position:relative; height:10px; background:rgba(255,255,255,0.08); border-radius:5px; margin-bottom:24px; overflow:hidden;">
                <!-- Underweight section -->
                <div style="position:absolute; left:0; top:0; bottom:0; width:28.3%; background:#3b82f6; opacity:0.75;"></div>
                <!-- Normal section -->
                <div style="position:absolute; left:28.3%; top:0; bottom:0; width:21.3%; background:#10b981; opacity:0.75;"></div>
                <!-- Overweight section -->
                <div style="position:absolute; left:49.6%; top:0; bottom:0; width:16.7%; background:#f59e0b; opacity:0.75;"></div>
                <!-- Obese section -->
                <div style="position:absolute; left:66.3%; top:0; bottom:0; right:0; background:#ef4444; opacity:0.75;"></div>
                
                <!-- Sliding Marker Pin -->
                <div style="position:absolute; left:{marker_pct}%; top:0; bottom:0; width:6px; background:#ffffff; box-shadow:0 0 10px #ffffff; transform:translateX(-50%); border-radius:3px;"></div>
            </div>
            
            <div style="font-weight:600; color:#e2e8f0; margin-bottom:6px;">Personal Recommendations:</div>
            <div style="color:#94a3b8; line-height:1.6; font-size:0.95rem;">{advice}</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  AI CHATBOT
# ══════════════════════════════════════════════════════════════════════════
elif page == "AI Chatbot":
    st.markdown('<div class="page-title">🤖 AI Health Assistant</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Ask me anything about your health</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Disclaimer</strong> — This assistant provides <em>general health information only</em>.
        It does not diagnose conditions or replace professional medical advice.
        Always consult a healthcare provider for serious concerns.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Chat container
    chat_container = st.container()

    # Input
    user_input = st.chat_input("Describe your symptom or ask a health question…")

    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )
        # Pass history for context-aware responses
        response = agent.get_health_advice(
            user_input, chat_history=st.session_state.chat_history
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    # Render chat
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:48px 24px;">
                <div style="font-size:3rem; margin-bottom:12px;">💬</div>
                <div style="font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-bottom:8px;">
                    Start a Conversation
                </div>
                <div style="color:#64748b; font-size:0.9rem; max-width:400px; margin:0 auto; line-height:1.6;">
                    Ask about headaches, medications, sleep tips, nutrition,
                    stress management, and more.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    if msg["role"] == "assistant" and msg["content"].startswith("🚨"):
                        st.markdown(f"""
                        <div style="background:rgba(239, 68, 68, 0.08); border: 2px solid #ef4444; border-radius: 12px; padding: 18px; color: #fecaca; margin: 8px 0; line-height: 1.6;">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(msg["content"])

    # Clear button
    if st.session_state.chat_history:
        _, btn_col = st.columns([9, 1])
        with btn_col:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
#  ABOUT
# ══════════════════════════════════════════════════════════════════════════
elif page == "About":
    st.markdown('<div class="page-title">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Healthcare Monitoring AI Agent — v2.5</div>',
                unsafe_allow_html=True)

    # Feature showcase
    features = [
        ("💊", "Medication Adherence",
         "Schedule, manage, track daily adherence, and log when taken."),
        ("⏰", "Smart Reminders",
         "Intelligent ±5 min reminder window so you never miss a dose."),
        ("📝", "Logs & Moods",
         "Journal symptoms, notes, and track your emotional wellness with visual graphs."),
        ("🤖", "AI Assistant",
         "Context-aware chatbot that knows your meds, recent logs, and detects emergencies."),
    ]

    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Tech stack
    st.markdown('<div class="section-header">🛠️ Tech Stack</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:700; color:#00d4ff; margin-bottom:12px;">Frontend & Backend</div>
            <div style="color:#94a3b8; line-height:2;">
                ▸ Streamlit (Python)<br>
                ▸ Custom CSS Glassmorphism UI<br>
                ▸ SQLite Database with multi-table tracking<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight:700; color:#7c3aed; margin-bottom:12px;">AI & Intelligence</div>
            <div style="color:#94a3b8; line-height:2;">
                ▸ OpenAI GPT-3.5 Turbo (optional)<br>
                ▸ Offline Word-boundary regex engine<br>
                ▸ Offline Emergency symptom detector<br>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        ⚠️ <strong>Important Disclaimer</strong><br>
        This application is for <em>educational and general information purposes only</em>.
        It does <strong>not</strong> provide medical diagnosis and does <strong>not</strong>
        replace professional medical advice. Always consult a qualified healthcare provider
        for serious health concerns.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    Healthcare AI Agent v2.5 · Built with Streamlit & Python · For demo purposes only
</div>
""", unsafe_allow_html=True)
