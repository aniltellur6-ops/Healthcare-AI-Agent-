import sqlite3
import os  # pyrefly: ignore
import csv  # pyrefly: ignore
import io  # pyrefly: ignore
from datetime import datetime, date  # pyrefly: ignore

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'health.db')


def _ensure_data_dir():
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(DB_PATH)
    os.makedirs(data_dir, exist_ok=True)


def get_db_connection():
    """Create database connection."""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Medications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            time_scheduled TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Health logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_note TEXT,
            symptom TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Medication reminders table (tracks when reminders were given)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            reminder_time TEXT NOT NULL,
            reminded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications(id)
        )
    ''')

    # --- NEW: Medication adherence tracking ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medication_taken (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medication_id) REFERENCES medications(id)
        )
    ''')

    # --- NEW: Water intake tracking ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            glasses INTEGER DEFAULT 1,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- NEW: Mood tracking ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  MEDICATIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_medication(name, dosage, time_scheduled):
    """Add a new medication."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medications (name, dosage, time_scheduled)
        VALUES (?, ?, ?)
    ''', (name, dosage, time_scheduled))
    conn.commit()
    conn.close()


def get_medications():
    """Get all active medications."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medications WHERE is_active = 1 ORDER BY time_scheduled')
    medications = cursor.fetchall()
    conn.close()
    return medications


def delete_medication(med_id):
    """Soft delete a medication."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE medications SET is_active = 0 WHERE id = ?', (med_id,))
    conn.commit()
    conn.close()


def get_medication_by_id(med_id):
    """Get a specific medication by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM medications WHERE id = ?', (med_id,))
    medication = cursor.fetchone()
    conn.close()
    return medication


# ═══════════════════════════════════════════════════════════════════════════
#  HEALTH LOGS
# ═══════════════════════════════════════════════════════════════════════════

def log_health_note(user_note, symptom=""):
    """Log a health note."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_logs (user_note, symptom)
        VALUES (?, ?)
    ''', (user_note, symptom))
    conn.commit()
    conn.close()


def get_health_logs():
    """Get recent health logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_logs ORDER BY logged_at DESC LIMIT 20')
    logs = cursor.fetchall()
    conn.close()
    return logs


# ═══════════════════════════════════════════════════════════════════════════
#  REMINDERS
# ═══════════════════════════════════════════════════════════════════════════

def record_reminder(medication_id):
    """Record that a reminder was shown."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reminders (medication_id, reminder_time)
        VALUES (?, ?)
    ''', (medication_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════════════
#  MEDICATION ADHERENCE (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def mark_medication_taken(medication_id):
    """Record that a medication was taken."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medication_taken (medication_id)
        VALUES (?)
    ''', (medication_id,))
    conn.commit()
    conn.close()


def is_medication_taken_today(medication_id):
    """Check if a specific medication was taken today."""
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as cnt FROM medication_taken
        WHERE medication_id = ? AND DATE(taken_at) = ?
    ''', (medication_id, today_str))
    row = cursor.fetchone()
    conn.close()
    return row['cnt'] > 0


def get_today_adherence():
    """
    Get today's medication adherence stats.
    Returns (taken_count, total_count).
    """
    today_str = date.today().isoformat()
    meds = get_medications()
    total = len(meds)
    if total == 0:
        return 0, 0

    taken = 0
    conn = get_db_connection()
    cursor = conn.cursor()
    for med in meds:
        cursor.execute('''
            SELECT COUNT(*) as cnt FROM medication_taken
            WHERE medication_id = ? AND DATE(taken_at) = ?
        ''', (med['id'], today_str))
        row = cursor.fetchone()
        if row['cnt'] > 0:
            taken += 1
    conn.close()
    return taken, total


# ═══════════════════════════════════════════════════════════════════════════
#  WATER INTAKE (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def log_water(glasses=1):
    """Log water intake."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO water_intake (glasses)
        VALUES (?)
    ''', (glasses,))
    conn.commit()
    conn.close()


def get_today_water():
    """Get today's total water intake in glasses."""
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(glasses), 0) as total
        FROM water_intake
        WHERE DATE(logged_at) = ?
    ''', (today_str,))
    row = cursor.fetchone()
    conn.close()
    return row['total']


# ═══════════════════════════════════════════════════════════════════════════
#  MOOD TRACKING (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def log_mood(mood):
    """Log current mood."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mood_logs (mood)
        VALUES (?)
    ''', (mood,))
    conn.commit()
    conn.close()


def get_recent_moods(days=7):
    """Get mood entries from the last N days."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mood, logged_at FROM mood_logs
        WHERE logged_at >= datetime('now', ?)
        ORDER BY logged_at DESC
    ''', (f'-{days} days',))
    moods = cursor.fetchall()
    conn.close()
    return moods


def get_today_mood():
    """Get the most recent mood logged today, or None."""
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT mood FROM mood_logs
        WHERE DATE(logged_at) = ?
        ORDER BY logged_at DESC LIMIT 1
    ''', (today_str,))
    row = cursor.fetchone()
    conn.close()
    return row['mood'] if row else None


# ═══════════════════════════════════════════════════════════════════════════
#  EXPORT (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def export_all_data_csv():
    """
    Export all health data as a CSV string.
    Returns a UTF-8 encoded bytes object for st.download_button.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Medications ---
    writer.writerow(["=== MEDICATIONS ==="])
    writer.writerow(["Name", "Dosage", "Scheduled Time", "Created At", "Active"])
    cursor.execute('SELECT * FROM medications ORDER BY created_at DESC')
    for row in cursor.fetchall():
        writer.writerow([
            row['name'], row['dosage'], row['time_scheduled'],
            row['created_at'], "Yes" if row['is_active'] else "No"
        ])
    writer.writerow([])

    # --- Health Logs ---
    writer.writerow(["=== HEALTH LOGS ==="])
    writer.writerow(["Date", "Note", "Symptom"])
    cursor.execute('SELECT * FROM health_logs ORDER BY logged_at DESC')
    for row in cursor.fetchall():
        writer.writerow([row['logged_at'], row['user_note'], row['symptom'] or ""])
    writer.writerow([])

    # --- Mood Logs ---
    writer.writerow(["=== MOOD LOGS ==="])
    writer.writerow(["Date", "Mood"])
    cursor.execute('SELECT * FROM mood_logs ORDER BY logged_at DESC')
    for row in cursor.fetchall():
        writer.writerow([row['logged_at'], row['mood']])
    writer.writerow([])

    # --- Water Intake ---
    writer.writerow(["=== WATER INTAKE ==="])
    writer.writerow(["Date", "Glasses"])
    cursor.execute('SELECT * FROM water_intake ORDER BY logged_at DESC')
    for row in cursor.fetchall():
        writer.writerow([row['logged_at'], row['glasses']])

    conn.close()
    return output.getvalue().encode('utf-8')


# ═══════════════════════════════════════════════════════════════════════════
#  AGENT CONTEXT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

def get_user_context_summary():
    """
    Build a plain-text summary of the user's active medications and recent
    health logs.  This is injected into the LLM prompt so the agent can
    give personalised answers.
    """
    lines = []

    # Active medications
    meds = get_medications()
    if meds:
        lines.append("Active medications:")
        for m in meds:
            taken = "taken today" if is_medication_taken_today(m['id']) else "not yet taken today"
            lines.append(f"  - {m['name']} {m['dosage']}, scheduled at {m['time_scheduled']} ({taken})")
    else:
        lines.append("No active medications.")

    # Adherence
    taken_count, total_count = get_today_adherence()
    if total_count > 0:
        pct = round(taken_count / total_count * 100)
        lines.append(f"Today's adherence: {taken_count}/{total_count} ({pct}%)")

    # Water
    water = get_today_water()
    lines.append(f"Water intake today: {water}/8 glasses")

    # Mood
    mood = get_today_mood()
    if mood:
        lines.append(f"Current mood: {mood}")

    # Recent health logs (last 5)
    logs = get_health_logs()
    if logs:
        lines.append("\nRecent health logs:")
        for log in logs[:5]:
            entry = f"  - [{log['logged_at']}] {log['user_note']}"
            if log['symptom']:
                entry += f" (symptom: {log['symptom']})"
            lines.append(entry)

    return "\n".join(lines)


# Initialize database on module load
_ensure_data_dir()
if not os.path.exists(DB_PATH):
    init_db()
