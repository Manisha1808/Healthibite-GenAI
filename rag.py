from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
import time
from google.genai import types
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

# 🗄️ Persistent Chroma DB
chroma_client = chromadb.Client(
    chromadb.config.Settings(persist_directory="./chroma_db")
)

collection = chroma_client.get_or_create_collection(name="health_data")


# 🧠 CLASSIFIER
def is_health_query(query):
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"""
Classify the query.

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

    ranked_docs = [doc for _, doc in sorted(
        zip(scores, docs),
        reverse=True
    )]

    return ranked_docs


# 🔁 FILTER
def filter_docs(query, docs):
    keywords = query.lower().split()

    filtered = []
    for doc in docs:
        if any(word in doc.lower() for word in keywords):
            filtered.append(doc)

    return filtered if filtered else docs


# 🔥 MAIN FUNCTION (USED BY FLASK)
def get_health_recommendation(query, age, goal, activity):
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    if not is_health_query(query):
        return "❌ I'm a health-focused assistant and can only help with health-related queries."

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=6
    )

    retrieved_docs = results['documents'][0]

    ranked_docs = rerank(query_embedding, retrieved_docs, embedding_model)
    filtered_docs = filter_docs(query, ranked_docs)

    context = "\n".join(filtered_docs[:3])

    prompt = f"""
You are a professional health assistant.

Your role is to provide advice ONLY related to:
- Health
- Diet
- Exercise
- Sleep
- Wellness
If goal is weight loss:
- suggest calorie deficit
- more cardio

If goal is muscle gain:
- suggest protein intake
- strength training

If activity level is low:
- start with light exercise

If activity level is high:
- suggest advanced routines
STRICT RULES:
1. If the user's query is NOT related to health, politely refuse.
2. Do NOT answer questions about programming, technology, general knowledge, or unrelated topics.
3. If unrelated, respond with:
   "I'm a health-focused assistant and can only help with health, diet, exercise, or sleep-related questions."

4. Use ONLY the provided context for generating answers.
5. Do NOT make up information outside the context.
6.Do NOT be overly strict. If there is ANY possible health interpretation, try to help.
7.If multiple issues are present, address all of them.



User Profile:
- Age: {age}
- Goal: {goal}
- Activity Level: {activity}

User problem:
{query}

Context:
{context}

Give personalized recommendations:

Diet:
- bullet points

Exercise:
- bullet points

Sleep:
- bullet points

Keep it concise and practical.
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
            print("Gemini error:", e)   # 🔥 SEE REAL ERROR
            time.sleep(2)

    if response and hasattr(response, "text"):
            return response.text
    else:
            return "⚠️ AI is busy. Try again in a few seconds."


# ✅ SAFETY
if __name__ == "__main__":
    print("Run app.py instead")
