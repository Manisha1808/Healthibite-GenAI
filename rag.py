from google import genai
import time
import os
from dotenv import load_dotenv
from database import save_history
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import json

def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text

# 🔑 Load environment variables
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ GEMINI_API_KEY not found")
    client = None
else:
    client = genai.Client(api_key=api_key)

# 📄 Load data safely
try:
    with open("data/health_docs.txt", "r", encoding="utf-8") as f:
        text = f.read()
except:
    text = ""

# ✂️ Chunking
def split_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

docs = split_text(text)

# 🧠 Lightweight TF-IDF (no torch)
vectorizer = TfidfVectorizer()

def get_embeddings(texts):
    return vectorizer.fit_transform(texts).toarray()

print("⚡ Lightweight RAG system ready")

# ⚡ CACHE GEMINI RESPONSES
def get_gemini_response(prompt):
    if client is None:
        return "ERROR: API key missing"

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        print("RAW RESPONSE:", response)
        return response.text

    except Exception as e:
        print("Gemini error:", e)
        return f"ERROR: {str(e)}"

# 🚨 SEVERITY DETECTOR
def detect_severity(query):
    severe_words = [
        "severe", "sharp pain", "vomiting", "blood",
        "chest pain", "fainting", "breathing difficulty",
        "extreme dizziness"
    ]

    moderate_words = [
        "persistent", "worsening", "constant pain",
        "several days", "3 days", "repeated"
    ]

    query_lower = query.lower()

    if any(word in query_lower for word in severe_words):
        return "severe"
    elif any(word in query_lower for word in moderate_words):
        return "moderate"
    else:
        return "mild"

# 🔥 MAIN FUNCTION
def get_health_recommendation(query, age, goal, activity):

    # ✅ SIMPLE RETRIEVAL (NO CHROMA, SAFE FOR DEPLOY)
    retrieved_docs = docs[:3]
    context = "\n".join(retrieved_docs)

    # Severity
    severity = detect_severity(query)

    # Dynamic rules
    dynamic_rules = ""

    if goal and goal.lower() == "weight management":
        dynamic_rules += """
If goal is weight loss:
- suggest calorie deficit
- recommend more cardio
- suggest exact low-calorie meals
"""

    elif goal and goal.lower() == "muscle gain":
        dynamic_rules += """
If goal is muscle gain:
- suggest protein-rich diet
- recommend strength training
"""

    if activity and activity.lower() == "low":
        dynamic_rules += """
If activity level is low:
- start with light exercise
"""

    elif activity and activity.lower() == "high":
        dynamic_rules += """
If activity level is high:
- recommend advanced routines
"""

    if severity == "severe":
        dynamic_rules += """
If symptoms appear severe:
- advise immediate medical consultation
"""

    elif severity == "moderate":
        dynamic_rules += """
If symptoms appear moderate:
- monitor and consult doctor if persists
"""

    else:
        dynamic_rules += """
If symptoms appear mild:
- focus on home care and lifestyle
"""

    # Prompt
    prompt = f"""
You are a professional health assistant.

Your role is to provide advice ONLY related to:
- Health
- Diet
- Exercise
- Sleep
- Wellness

{dynamic_rules}

IMPORTANT RESPONSE STYLE:
- Respond in a professional healthcare advisory tone
- Recommendations should sound medically informed, clear, and trustworthy
- Each recommendation must explain WHY it helps
- Keep advice concise but professional
- Sound like a real nutrition expert speaking to a patient

IMPORTANT OUTPUT FORMAT:

Return ONLY valid JSON in exactly this format:

{{
  "diet": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "exercise": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ],
  "sleep": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ]
}}

STRICT RULES:
- Return JSON only
- No markdown
- No extra text before JSON
- No extra text after JSON
- Do NOT repeat sections
- Do NOT include diet inside sleep
- Do NOT include exercise inside sleep
- Each section must contain only its own advice
- Keep answers concise and practical
- If unrelated, respond with: "I'm a health-focused assistant and can only help with health, diet, exercise, or sleep-related questions."

RESPONSE QUALITY RULES:
- Keep recommendations professional, medically informed, and practical
- Provide specific food examples instead of generic categories
- Explain briefly why each recommendation helps
- Avoid vague phrases like "eat healthy food"
- Keep each recommendation between 1–2 concise professional sentences
- Avoid overly academic wording
- Sound like a real nutrition expert speaking to a patient


User:
{query}

Context:
{context}
"""

    # Gemini
    response_text = None

    for _ in range(3):
        response_text = get_gemini_response(prompt)

        if response_text and not str(response_text).startswith("ERROR"):
           break


        print("Retrying Gemini...")
        time.sleep(2)
    print("FINAL RESPONSE:", response_text)
    if response_text and not str(response_text).startswith("ERROR"):
          cleaned = clean_json_response(response_text)

          try:
              parsed = json.loads(cleaned)
          except Exception as e:
              
              print("⚠️ Invalid JSON from AI, using fallback")

              parsed = {
        "diet": [
            "Eat simple, home-cooked meals like rice, dal, vegetables, and fruits.",
            "Stay hydrated and avoid processed or heavy foods.",
            "Include light and easily digestible meals throughout the day."
        ],
        "exercise": [
            "Do light walking for 15–20 minutes daily.",
            "Avoid heavy workouts if you are not feeling well.",
            "Stretch your body gently to reduce stiffness."
        ],
        "sleep": [
            "Maintain 7–8 hours of sleep.",
            "Avoid screens before bedtime.",
            "Keep a consistent sleep schedule."
        ]
    }

              cleaned = json.dumps(parsed)

    # Save history
          try:
              save_history(query, age, goal, activity, severity, cleaned)
          except Exception as e:
              print("Save history failed:", e)

          return cleaned

    return json.dumps({
    "diet": ["⚠️ Unable to generate response right now."],
    "exercise": ["Please try again in a moment."],
    "sleep": ["If issue persists, check API or logs."]
})


if __name__ == "__main__":
    print("Run app.py instead")