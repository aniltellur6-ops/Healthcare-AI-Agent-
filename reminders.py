from datetime import datetime


def check_reminders(medications):
    """
    Check if any medications are due for a reminder.
    Uses a ±5 minute window so reminders aren't missed if the page
    loads a few seconds late.
    Returns list of medications that should be reminded now.
    """
    now = datetime.now()
    current_minutes = now.hour * 60 + now.minute
    due_medications = []

    for med in medications:
        scheduled_time = med['time_scheduled']
        try:
            parts = scheduled_time.split(":")
            sched_minutes = int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            continue

        # ±5 minute window
        diff = abs(current_minutes - sched_minutes)
        # Handle midnight wrap-around
        diff = min(diff, 1440 - diff)

        if diff <= 5:
            due_medications.append(med)

    return due_medications


def format_medication_display(medication):
    """Format medication data for display."""
    return {
        'id': medication['id'],
        'name': medication['name'],
        'dosage': medication['dosage'],
        'time': medication['time_scheduled'],
        'created': medication['created_at']
    }


def get_reminder_message(medication):
    """Generate a reminder message for a medication."""
    return (
        f"⏰ **MEDICATION REMINDER** — "
        f"**{medication['name']}** ({medication['dosage']}) "
        f"scheduled at {medication['time_scheduled']}. "
        f"Please take your medication now."
    )


def validate_time_format(time_str):
    """Validate time format (HH:MM)."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def validate_medication_input(name, dosage, time_scheduled):
    """Validate medication input."""
    if not name or not name.strip():
        return False, "Medication name is required"
    if not dosage or not dosage.strip():
        return False, "Dosage is required"
    if not validate_time_format(time_scheduled):
        return False, "Time must be in HH:MM format (e.g., 08:30)"
    return True, "Valid"
