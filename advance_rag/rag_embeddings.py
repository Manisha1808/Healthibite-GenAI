from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
import time
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# 🔑 Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 📄 Load data
with open("data/health_docs.txt", "r") as f:
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
embedding_model = SentenceTransformer("all-MiniLM-L6-v2",local_files_only=True)

# 🗄️ Load Persistent Chroma DB ONLY
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="health_data")

print("⚡ Loaded precomputed embeddings successfully!")


# 🧠 CLASSIFIER
def is_health_query(query):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"""
Return ONLY one word:
HEALTH or NON_HEALTH

Query: {query}
"""
        )
        return "HEALTH" in response.text.upper()
    except:
        return True


# 🔁 RERANK
def rerank(query_embedding, docs, embedding_model):
    doc_embeddings = [embedding_model.encode(doc) for doc in docs]

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


# 🔥 MAIN FUNCTION
def get_health_recommendation(query, age, goal, activity):

    if not is_health_query(query):
        return "❌ I'm a health-focused assistant and can only help with health-related queries."

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=6
    )

    retrieved_docs = results["documents"][0]

    ranked_docs = rerank(query_embedding, retrieved_docs, embedding_model)
    filtered_docs = filter_docs(query, ranked_docs)

    context = "\n".join(filtered_docs[:3])

    # 🔥 Dynamic Prompt Rules
    dynamic_rules = ""

    if goal.lower() == "weight management":
        dynamic_rules += """
If goal is weight loss:
- suggest calorie deficit
- recommend more cardio
"""

    elif goal.lower() == "muscle gain":
        dynamic_rules += """
If goal is muscle gain:
- suggest protein-rich diet
- recommend strength training
"""

    if activity.lower() == "low":
        dynamic_rules += """
If activity level is low:
- start with light exercise
"""

    diet_keywords = ["food", "diet", "eat", "nutrition"]

    if any(word in query.lower() for word in diet_keywords):
        dynamic_rules += """
If query asks for diet advice:
- focus on food recommendations
"""

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

- Respond in a professional healthcare advisory tone.
- Recommendations should sound medically informed, clear, and trustworthy.
- Avoid casual or vague wording.
- Each recommendation must explain WHY it helps.
- Keep advice concise but professional.
- Use simple language understandable to general users.
- Avoid robotic repetition.
- Make each section sound like expert wellness guidance.

IMPORTANT OUTPUT FORMAT:

Return ONLY valid JSON in exactly this format:

{{
  "diet": [
    "Professional recommendation 1",
    "Professional recommendation 2",
    "Professional recommendation 3"
  ],
  "exercise": [
    "Professional recommendation 1",
    "Professional recommendation 2",
    "Professional recommendation 3"
  ],
  "sleep": [
    "Professional recommendation 1",
    "Professional recommendation 2",
    "Professional recommendation 3"
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

User Profile:
- Age: {age}
- Goal: {goal}
- Activity Level: {activity}

User problem:
{query}

Context:
{context}
"""


    response = None

    for i in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            break
        except Exception as e:
            print("Gemini error:", e)

            if "429" in str(e):
                return "AI_BUSY"

            time.sleep(2)

    if response and hasattr(response, "text"):
          cleaned = response.text.replace("```json", "").replace("```", "").strip()

          print("\n==============================")
          print("RAW GEMINI OUTPUT:")
          print(cleaned)
          print("==============================\n")

          return cleaned
    else:
          return "AI_BUSY"


# ✅ SAFETY
if __name__ == "__main__":
    print("Run app.py instead") 
