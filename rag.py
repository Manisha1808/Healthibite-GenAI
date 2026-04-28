import google.generativeai as genai
import time
import os
from dotenv import load_dotenv
from database import save_history
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import json

# -------------------------------
# LOAD ENV
# -------------------------------
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ GEMINI_API_KEY not found")
    client = None
else:
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel("gemini-3-flash-preview")

# -------------------------------
# CLEAN JSON
# -------------------------------
def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text

# -------------------------------
# LOAD DATA
# -------------------------------
try:
    with open("data/health_docs.txt", "r", encoding="utf-8") as f:
        text = f.read()
except:
    text = ""

# -------------------------------
# CHUNKING
# -------------------------------
def split_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

docs = split_text(text)

# -------------------------------
# VECTORIZER
# -------------------------------
vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(docs)

print("⚡ Lightweight RAG system ready")

# -------------------------------
# GEMINI CALL
# -------------------------------
def get_gemini_response(prompt):
    if client is None:
        return "ERROR: API key missing"

    try:
        response = client.generate_content(prompt)

        print("FULL RESPONSE:", response)

        if hasattr(response, "text") and response.text:
            return response.text
        else:
            return str(response)

    except Exception as e:
        print("Gemini error:", e)
        return f"ERROR: {str(e)}"

# -------------------------------
# SEVERITY
# -------------------------------
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

# -------------------------------
# MAIN FUNCTION
# -------------------------------
def get_health_recommendation(query, age, goal, activity):

    query_vec = vectorizer.transform([query])
    scores = (doc_vectors * query_vec.T).toarray()

    top_indices = scores.flatten().argsort()[-3:][::-1]
    retrieved_docs = [docs[i] for i in top_indices]

    context = "\n".join(retrieved_docs)

    severity = detect_severity(query)

    dynamic_rules = ""

    if goal and goal.lower() == "weight management":
        dynamic_rules += "Suggest calorie deficit and cardio.\n"
    elif goal and goal.lower() == "muscle gain":
        dynamic_rules += "Suggest protein-rich diet and strength training.\n"

    if activity == "low":
        dynamic_rules += "Start with light exercise.\n"
    elif activity == "high":
        dynamic_rules += "Recommend advanced routines.\n"

    if severity == "severe":
        dynamic_rules += "Advise immediate medical consultation.\n"

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


    response_text = get_gemini_response(prompt)

    if response_text.startswith("ERROR"):
        return json.dumps({
            "diet": ["Unable to generate response"],
            "exercise": ["Try again"],
            "sleep": ["Check API"]
        })

    cleaned = clean_json_response(response_text)

    try:
        parsed = json.loads(cleaned)
    except:
        parsed = {
            "diet": ["Simple home food"],
            "exercise": ["Light walking"],
            "sleep": ["7-8 hours sleep"]
        }

    try:
        save_history(query, age, goal, activity, severity, json.dumps(parsed))
    except Exception as e:
        print("Save failed:", e)

    return json.dumps(parsed)