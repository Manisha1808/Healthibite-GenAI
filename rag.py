from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
import time
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv
from functools import lru_cache
from database import save_history
# 🔑 Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 📄 Load data
with open("data/health_docs.txt", "r", encoding="utf-8") as f:
    text = f.read()


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

# 🧠 Load embedding model ONCE
embedding_model = None

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("Loading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return embedding_model

# 🗄️ Load Persistent Chroma DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

collection = None

def get_collection():
    global collection
    if collection is None:
        print("Loading Chroma DB...")
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name="health_data")
    return collection
print("⚡ Loaded precomputed embeddings successfully!")


# ⚡ CACHE GEMINI RESPONSES
@lru_cache(maxsize=100)
def cached_gemini_response(prompt):
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text


# 🔁 RERANK
def rerank(query_embedding, docs, doc_embeddings):
    scores = cosine_similarity(
        [query_embedding],
        doc_embeddings
    )[0]

    ranked_docs = [
        doc for _, doc in sorted(
            zip(scores, docs),
            reverse=True
        )
    ]

    return ranked_docs


# 🔁 FILTER
def filter_docs(query, docs):
    keywords = query.lower().split()

    filtered = []
    for doc in docs:
        if any(word in doc.lower() for word in keywords):
            filtered.append(doc)

    return filtered if filtered else docs


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

    # Generate query embedding
    model = get_embedding_model()
    query_embedding = model.encode(query)

    # Faster retrieval: reduced from 6 → 3
    collection = get_collection()

    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "embeddings"]
)

    retrieved_docs = results["documents"][0]
    retrieved_embeddings = results["embeddings"][0]

    ranked_docs = rerank(
    query_embedding,
    retrieved_docs,
    retrieved_embeddings )
    filtered_docs = filter_docs(query, ranked_docs)

    context = "\n".join(filtered_docs[:3])

    # 🚨 Detect symptom severity
    severity = detect_severity(query)

    # 🔥 Dynamic Prompt Rules
    dynamic_rules = ""

    # Goal-based rules
    if goal.lower() == "weight management":
        dynamic_rules += """
If goal is weight loss:
- suggest calorie deficit
- recommend more cardio
- suggest exact low-calorie meals
"""

    elif goal.lower() == "muscle gain":
        dynamic_rules += """
If goal is muscle gain:
- suggest protein-rich diet
- recommend strength training
"""

    # Activity-based rules
    if activity.lower() == "low":
        dynamic_rules += """
If activity level is low:
- start with light exercise
"""

    elif activity.lower() == "high":
        dynamic_rules += """
If activity level is high:
- recommend advanced exercise routines
"""

    # Severity rules
    if severity == "severe":
        dynamic_rules += """
If symptoms appear severe:
- strongly advise immediate medical consultation
- mention urgent warning signs clearly
"""

    elif severity == "moderate":
        dynamic_rules += """
If symptoms appear moderate:
- advise monitoring symptoms closely
- recommend medical consultation if symptoms persist
"""

    else:
        dynamic_rules += """
If symptoms appear mild:
- focus on home-care, diet, and lifestyle improvements
"""

    # Diet-specific rules
    diet_keywords = ["food", "diet", "eat", "nutrition", "meal"]

    if any(word in query.lower() for word in diet_keywords):
        dynamic_rules += """
If query asks for diet advice:
- focus on specific meal recommendations
- include breakfast, lunch, dinner examples
"""

    # 🔥 Prompt
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
- Each section must contain only its own advice
- If unrelated, politely refuse health-unrelated query

User Profile:
- Age: {age}
- Goal: {goal}
- Activity Level: {activity}

User Problem:
{query}

Context:
{context}
"""

    # ⚡ OPTIMIZED RESPONSE GENERATION WITH CACHE
    response_text = None

    for i in range(3):
        try:
            response_text = cached_gemini_response(prompt)
            break

        except Exception as e:
            print("Gemini error:", e)

            if "429" in str(e):
                return "AI_BUSY"

            time.sleep(2)

    if response_text:
        cleaned = response_text.replace("```json", "").replace("```", "").strip()

        print("\n==============================")
        print("RAW GEMINI OUTPUT:")
        print(cleaned)
        print("==============================\n")

        save_history(
    query,
    age,
    goal,
    activity,
    severity,
    cleaned
)

        return cleaned

    else:
        return "AI_BUSY"


# ✅ SAFETY
if __name__ == "__main__":
    print("Run app.py instead")


