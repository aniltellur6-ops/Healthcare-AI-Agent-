"""
Healthcare AI Agent — fast, context-aware health assistant.

Priority order:
  1. Emergency symptom detection (instant, highest priority)
  2. Word-boundary keyword matching (instant, offline)
  3. OpenAI gpt-3.5-turbo with conversation memory + user context (if API key set)
  4. Helpful fallback topic list (no crash)
"""

from __future__ import annotations

import os  # pyrefly: ignore
import re  # pyrefly: ignore
from dotenv import load_dotenv  # pyrefly: ignore [missing-import]

load_dotenv()

# ---------------------------------------------------------------------------
# Emergency patterns — checked FIRST, before any keyword matching
# ---------------------------------------------------------------------------
EMERGENCY_KEYWORDS = [
    # Cardiac
    r"heart\s*attack",
    r"cardiac\s*arrest",
    r"chest\s*pain.{0,30}(breath|sweat|nausea|arm|jaw)",
    r"(can'?t|cannot|unable\s+to)\s+breathe",
    r"difficulty\s+breathing.{0,20}(severe|extreme|worst)",
    r"(severe|extreme|crushing)\s+chest\s*pain",
    # Stroke
    r"stroke",
    r"(face|arm|speech)\s+(droop|numb|slur)",
    r"sudden.{0,20}(paralysis|numbness|confusion|vision\s+loss)",
    # Severe bleeding / trauma
    r"(severe|heavy|uncontrollable|won'?t\s+stop)\s+bleeding",
    r"(deep|large)\s+(cut|wound|gash)",
    # Poisoning / overdose
    r"(overdose|poisoning|swallowed\s+poison)",
    r"(took|swallowed)\s+(too\s+many|whole\s+bottle)",
    # Unconsciousness
    r"(unconscious|not\s+breathing|no\s+pulse|passed\s+out|fainted.{0,15}not\s+waking)",
    r"(seizure|convulsion)s?\s+(won'?t\s+stop|lasting)",
    # Suicidal ideation
    r"(want\s+to|going\s+to|thinking\s+of)\s+(die|kill\s+my|end\s+(my\s+)?life|suicide)",
    r"self[\s-]?harm",
    # Allergic reaction
    r"(anaphylaxis|anaphylactic)",
    r"(throat|tongue|face)\s+(swell|closing|swollen).{0,20}(can'?t|breath)",
    # Severe pain
    r"(worst|unbearable|10.{0,5}10)\s+pain.{0,15}(ever|life)",
]

_EMERGENCY_PATTERNS = [
    re.compile(pat, re.IGNORECASE) for pat in EMERGENCY_KEYWORDS
]

EMERGENCY_RESPONSE = """🚨 **EMERGENCY — SEEK IMMEDIATE HELP**

Based on what you've described, this may be a **medical emergency**.

🔴 **Call emergency services NOW:**
- 🇮🇳 India: **112** or **108** (Ambulance)
- 🇺🇸 USA: **911**
- 🇬🇧 UK: **999**
- 🌍 International: **112**

**While waiting for help:**
1. Stay calm and remain still
2. Do not eat or drink anything
3. If conscious, sit or lie in a comfortable position
4. Loosen any tight clothing
5. Have someone stay with you

⚠️ **This app cannot handle emergencies. Professional medical help is critical.**
"""

# ---------------------------------------------------------------------------
# Predefined health responses (used for instant keyword matching)
# ---------------------------------------------------------------------------
HEALTH_RESPONSES = {
    # Headaches and migraines
    "headache": "For headaches: Rest in a quiet, dark room and drink water. Apply a cold or warm compress. Take over-the-counter pain relief if needed. Avoid bright lights and loud noise. If severe or recurring, consult a doctor.",
    "migraine": "For migraines: Find a quiet dark place to rest. Stay hydrated and apply ice packs. Avoid triggers like certain foods, stress, or weather changes. If frequent, consult a neurologist.",

    # Cold and flu
    "cold": "For cold symptoms: Get plenty of rest, stay hydrated, use saline nasal drops, and take vitamin C. Use a humidifier to ease congestion. Most colds improve within 7-10 days. See a doctor if symptoms worsen.",
    "cough": "For coughs: Stay hydrated, use honey or lozenges, elevate your head while sleeping. Use a humidifier to ease congestion. If cough persists beyond 3 weeks or worsens, consult a doctor.",
    "flu": "For flu symptoms: Rest, hydrate, and manage fever with acetaminophen or ibuprofen if needed. Avoid close contact with others. Seek urgent care if you have severe symptoms.",
    "congestion": "For congestion: Use saline nasal drops or spray, drink warm liquids, use a humidifier, and elevate your head. Avoid dairy products which may increase mucus.",
    "sore throat": "For sore throat: Gargle with salt water, drink warm liquids, use lozenges, and get rest. Apply a warm compress. If accompanied by fever or lasts over a week, see a doctor.",

    # Fever and temperature
    "fever": "For fever: Drink plenty of fluids, rest, and use fever-reducing medication if discomfort persists. Wear light clothing. Monitor temperature regularly. Seek immediate care if fever exceeds 103°F or lasts beyond 3 days.",

    # Digestive issues
    "heartburn": "For heartburn: Avoid spicy, fatty, and acidic foods. Eat smaller, frequent meals. Stay upright after eating for 2-3 hours. Try antacids if needed. Consult a doctor if frequent.",
    "nausea": "For nausea: Sip clear liquids slowly, eat small portions of bland foods (crackers, toast), and rest. Use ginger tea which may help. Avoid strong smells and sudden movements.",
    "stomach pain": "For stomach pain: Rest, apply a heating pad, stay hydrated, and eat bland foods. Avoid dairy, fatty, or spicy foods. Seek medical help if pain is severe or accompanied by fever.",
    "diarrhea": "For diarrhea: Stay hydrated with electrolyte solutions, eat bland foods (rice, bananas, toast), and rest. Avoid dairy and fatty foods. If it persists beyond 3 days or is severe, consult a doctor.",
    "constipation": "For constipation: Increase water intake, eat fiber-rich foods (fruits, vegetables, whole grains), and exercise regularly. Try gentle abdominal massage. If persistent, consult a doctor.",
    "indigestion": "For indigestion: Eat smaller, frequent meals, chew slowly, and avoid trigger foods. Stay upright after eating. Use antacids if needed. Reduce stress and caffeine intake.",

    # Pain conditions
    "back pain": "For back pain: Use heat or ice therapy, maintain good posture, and do gentle stretching. Over-the-counter pain relief may help. Avoid heavy lifting. If severe or persistent, see a physical therapist or doctor.",
    "neck pain": "For neck pain: Apply heat, do gentle stretching, maintain good posture, and use a supportive pillow. Use pain relief if needed. If accompanied by numbness or weakness, seek medical help.",
    "joint pain": "For joint pain: Rest the affected joint, apply ice for acute pain or heat for chronic pain, and elevate if possible. Compression bandages may help. Consult a doctor if pain persists or worsens.",
    "muscle pain": "For muscle pain: Rest, apply ice initially (first 48 hours), then heat. Gentle stretching and massage may help. Use over-the-counter pain relief if needed. Gradual movement aids recovery.",
    "chest pain": "Chest pain can be serious. If sudden, severe, or accompanied by shortness of breath, sweating, or nausea, call emergency services immediately. For mild, intermittent pain, consult your doctor promptly.",
    "pain": "For pain: Identify the type and location. Rest the affected area, apply appropriate temperature therapy, and use pain relief medication if needed. Gentle movement aids recovery. Consult a doctor if severe or persistent.",

    # Sleep issues
    "sleep": "For better sleep: Maintain a consistent schedule, create a dark, cool, quiet bedroom, avoid screens 1-2 hours before bed, and limit caffeine. Try relaxation techniques like deep breathing or meditation.",
    "insomnia": "For insomnia: Maintain consistent sleep/wake times, avoid caffeine and heavy meals before bed, exercise regularly, and create a relaxing bedtime routine. Try meditation or deep breathing. If persistent, consult a sleep specialist.",
    "tired": "If you're tired: Ensure you get 7-9 hours of quality sleep, stay hydrated, exercise regularly, and eat balanced meals. Limit screen time before bed. If fatigue persists, consult a doctor.",
    "fatigue": "For fatigue: Prioritise sleep hygiene, balanced nutrition, and regular exercise. Stay hydrated and manage stress. If fatigue is chronic or sudden, consult a healthcare provider to rule out underlying conditions.",

    # Mental health
    "stress": "For stress management: Practice deep breathing, meditation, or yoga. Exercise regularly, maintain social connections, and take breaks. Talk to someone you trust or seek professional help if overwhelmed.",
    "anxiety": "For anxiety: Practice breathing exercises (4-7-8 breathing), meditation, and grounding techniques. Regular exercise helps. Limit caffeine and maintain sleep hygiene. Professional counseling can be very helpful.",
    "depression": "For depression: Stay physically active, maintain social connections, maintain a routine, and practice self-care. Consider talking to a therapist or counselor. If thoughts of self-harm occur, reach out to emergency services immediately.",

    # Allergies and skin
    "allergy": "For allergies: Identify and avoid triggers, use antihistamines, and rinse nasal passages with saline. Keep windows closed during high pollen seasons. Use air filters. If severe, consult an allergist.",
    "rash": "For skin rash: Keep the affected area clean and dry. Avoid irritants and fragrances. Use cool compresses if itchy. Use appropriate topical cream if needed. If spreads, persists, or worsens, see a doctor.",
    "acne": "For acne: Wash face twice daily with gentle cleanser, avoid touching your face, use non-comedogenic products, and maintain good hygiene. Over-the-counter treatments may help. For severe acne, see a dermatologist.",

    # Respiratory
    "breathing": "For breathing difficulties: Sit upright and take slow, deep breaths. If shortness of breath occurs at rest or is severe, seek emergency care immediately. For persistent issues, consult a pulmonologist.",
    "asthma": "For asthma: Use prescribed inhalers as directed, avoid triggers, stay hydrated, and maintain a clean environment. Keep rescue inhaler accessible. If symptoms worsen, contact your doctor.",

    # Lifestyle
    "exercise": "Regular exercise benefits: Aim for 150 minutes of moderate activity per week plus strength training. Start gradually, warm up, and cool down. Choose activities you enjoy. Always consult your doctor before starting new programs.",
    "diet": "For healthy diet: Eat balanced meals with fruits, vegetables, whole grains, and proteins. Limit salt, sugar, and saturated fats. Stay hydrated. Portion control is important. Consider consulting a nutritionist.",
    "weight": "For healthy weight: Combine balanced nutrition with regular exercise. Include proteins and fiber in meals, eat slowly, and limit processed foods. Avoid crash diets. For significant concerns, consult a healthcare provider.",
    "nutrition": "For good nutrition: Eat a variety of foods from all groups. Include fruits (2-4 servings), vegetables (3-5 servings), grains, proteins, and dairy. Limit unhealthy fats, sugar, and salt.",
    "hydration": "For proper hydration: Aim for 8 glasses (about 2 litres) of water daily. Increase intake during exercise, hot weather, or illness. Watch for signs of dehydration: dark urine, dry mouth, dizziness.",
    "vitamin": "For vitamins: A balanced diet usually provides enough. Key ones include Vitamin D (sunlight + fortified foods), B12, Iron, and Omega-3s. Consult a doctor before starting supplements.",

    # General
    "medication": "For medications: Always take as prescribed by your doctor. Don't skip doses or adjust dosage without consulting. Report side effects immediately. Keep medications stored properly. Use pill organizers to remember doses.",
    "first aid": "Basic first aid: For cuts — clean with water, apply pressure, bandage. For burns — cool with running water 10+ minutes. For sprains — rest, ice, compress, elevate (RICE). Call emergency services for serious injuries.",
    "blood pressure": "For blood pressure: Monitor regularly. Reduce sodium intake, exercise 30+ minutes daily, limit alcohol, manage stress, and maintain a healthy weight. Take prescribed medication consistently. Consult your doctor for persistent high or low readings.",
    "diabetes": "For diabetes management: Monitor blood sugar regularly, follow your meal plan, exercise consistently, take medications as prescribed, and attend regular check-ups. Watch for signs of hypo/hyperglycemia.",
    "bmi": "BMI (Body Mass Index) measures body fat based on height and weight. Ranges: <18.5 Underweight, 18.5-24.9 Normal, 25-29.9 Overweight, 30+ Obese. Use the BMI Calculator page in this app for a detailed analysis!",
}

# Pre-compile keyword patterns for word-boundary matching (fast)
_KEYWORD_PATTERNS: list[tuple[re.Pattern, str, int]] = []
for _kw, _resp in HEALTH_RESPONSES.items():
    _pat = re.compile(r"\b" + re.escape(_kw) + r"\b", re.IGNORECASE)
    _KEYWORD_PATTERNS.append((_pat, _resp, len(_kw)))


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------
class HealthAgent:
    """Fast, context-aware health assistant with emergency detection."""

    MAX_HISTORY = 10  # messages to include in LLM context

    SYSTEM_PROMPT = (
        "You are a friendly, professional health-information assistant embedded "
        "in a medication-tracking app. Rules:\n"
        "1. Provide general health information ONLY.\n"
        "2. NEVER diagnose conditions or prescribe medications.\n"
        "3. Keep responses concise (3-5 sentences).\n"
        "4. When the user's medication or health-log data is provided, "
        "reference it naturally to personalise your answer.\n"
        "5. Always suggest consulting a healthcare provider for serious concerns.\n"
        "6. Use a warm, reassuring tone.\n"
    )

    def __init__(self):
        """Initialize the health agent."""
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.use_llm = bool(self.api_key) and self.api_key != "your_openai_api_key_here"
        self._client = None

        if self.use_llm:
            try:
                # pyrefly: ignore [missing-import]
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, timeout=15.0)
            except Exception as exc:
                print(f"[HealthAgent] OpenAI init failed: {exc}. Using offline mode.")
                self.use_llm = False

    # ---- public API --------------------------------------------------------

    def get_health_advice(self, user_question: str,
                          chat_history: list | None = None) -> str:
        """
        Return health advice for *user_question*.

        0. Check for emergency symptoms (highest priority).
        1. Try word-boundary keyword match (instant).
        2. If no match and LLM available → call OpenAI with conversation context.
        3. Fallback → helpful topic list.
        """
        if not user_question or not user_question.strip():
            return "Please ask a health-related question."

        # --- Step 0: EMERGENCY detection (highest priority) ---
        if self._check_emergency(user_question):
            return EMERGENCY_RESPONSE

        # --- Step 1: keyword matching (instant) ---
        keyword_answer = self._match_keywords(user_question)
        if keyword_answer:
            return keyword_answer

        # --- Step 2: LLM with memory + user context ---
        if self.use_llm and self._client:
            try:
                return self._call_llm(user_question, chat_history)
            except Exception as exc:
                print(f"[HealthAgent] LLM error: {exc}")
                # fall through to fallback

        # --- Step 3: Fallback ---
        return self._fallback_response()

    def format_response(self, response: str) -> str:
        """Format response for display."""
        return f"🏥 **Health Agent**: {response}"

    @staticmethod
    def is_emergency_response(response: str) -> bool:
        """Check if a response is an emergency alert."""
        return response.startswith("🚨")

    # ---- private helpers ---------------------------------------------------

    @staticmethod
    def _check_emergency(question: str) -> bool:
        """Check if the question describes an emergency situation."""
        for pattern in _EMERGENCY_PATTERNS:
            if pattern.search(question):
                return True
        return False

    @staticmethod
    def _match_keywords(question: str) -> str | None:
        """
        Word-boundary keyword matching.  Returns the response for the
        longest matching keyword, or None.
        """
        best_response = None
        best_length = 0

        for pattern, response, length in _KEYWORD_PATTERNS:
            if pattern.search(question) and length > best_length:
                best_response = response
                best_length = length

        return best_response

    def _call_llm(self, question: str,
                  chat_history: list | None = None) -> str:
        """Call OpenAI with conversation memory and user context."""
        from db.database import get_user_context_summary

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Inject user context (medications & logs)
        user_ctx = get_user_context_summary()
        if user_ctx:
            messages.append({
                "role": "system",
                "content": f"User's health profile:\n{user_ctx}"
            })

        # Inject conversation history (last N messages)
        if chat_history:
            for msg in chat_history[-self.MAX_HISTORY:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Current question
        messages.append({"role": "user", "content": question})

        response = self._client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.6,
        )

        return response.choices[0].message.content.strip()

    @staticmethod
    def _fallback_response() -> str:
        return (
            "I can provide health information on many topics. Try asking about:\n\n"
            "💊 **Medications** — dosage tips, reminders\n"
            "🤒 **Symptoms** — headache, fever, cough, sore throat, nausea\n"
            "💪 **Pain** — back, neck, joint, muscle, chest pain\n"
            "🧠 **Mental Health** — stress, anxiety, sleep, fatigue\n"
            "🥗 **Lifestyle** — diet, exercise, hydration, vitamins\n"
            "🩺 **Conditions** — asthma, diabetes, blood pressure, allergies\n"
            "🩹 **First Aid** — cuts, burns, sprains\n\n"
            "Describe your concern and I'll do my best to help. "
            "For serious symptoms, always seek professional medical care."
        )


# Singleton instance
_agent = HealthAgent()


def get_agent() -> HealthAgent:
    """Get the health agent singleton."""
    return _agent
