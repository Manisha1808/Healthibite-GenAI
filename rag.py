from google import genai
import time
import os

# 🔑 API KEY
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 📄 Load data (lightweight use)
with open("data/health_docs.txt", "r") as f:
    text = f.read()


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


# 🔥 SIMPLE CONTEXT RETRIEVAL (LIGHTWEIGHT RAG)
def get_context(query):
    query = query.lower()

    relevant_lines = []
    for line in text.split("\n"):
        if any(word in line.lower() for word in query.split()):
            relevant_lines.append(line)

    return "\n".join(relevant_lines[:5]) if relevant_lines else "General health advice."


# 🔥 MAIN FUNCTION
def get_health_recommendation(query, age, goal, activity):

    if not is_health_query(query):
        return "❌ I'm a health-focused assistant and can only help with health-related queries."

    # 🔥 lightweight retrieval
    context = get_context(query)

    prompt = f"""
You are a professional health assistant.

STRICT RULES:
- Do NOT use markdown (** or *)
- Use simple bullet points with "-"
- Keep answers structured

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
            time.sleep(2)

    if response and hasattr(response, "text"):
        return response.text
    else:
        return "⚠️ AI is busy. Try again later."


# ✅ SAFETY
if __name__ == "__main__":
    print("Run app.py instead")
