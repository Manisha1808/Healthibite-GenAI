# 🥗 HealthiBite – AI-Powered Health Recommendation System
Built to simulate a real-world AI health assistant with structured, explainable outputs.


## 📌 Overview

HealthiBite is an AI-powered web application that provides **personalized lifestyle recommendations** based on user inputs such as age, fitness goals, activity level, and health concerns.

The system delivers structured, actionable insights across:
- 🥗 Diet
- 🏃 Exercise
- 😴 Sleep

It combines **Retrieval-Augmented Generation (RAG)** with Generative AI to produce context-aware recommendations.

---

🚀 **Live Demo: https://healthibite-genai.onrender.com

---
## 🚀 Project Highlights

- Built a full **Retrieval-Augmented Generation (RAG)** pipeline  
- Implemented **semantic search using vector similarity (TF-IDF / embeddings)**  
- Integrated **LLM-based structured output generation (Gemini API)**  
- Designed and deployed a **production-aware Flask application on Render**  
- Optimized system for **low-latency and free-tier deployment constraints**

---
## ✨ Features

- 🧠 Full **RAG (Retrieval-Augmented Generation)** pipeline using embeddings
- 🔍 Semantic search over health dataset using vector similarity
- 📊 Re-ranking of retrieved documents for improved relevance
- 🤖 AI-generated personalized recommendations
- 🎯 Structured output (Diet, Exercise, Sleep)
- 🗂️ User query history tracking using SQLite
- ⚡ Optimized lightweight deployment version for performance
- 🛡️ Handles API limits gracefully (AI busy state)
- 🎨 Modern UI with glassmorphism design

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Flask (Python)  
- **AI Integration:** Gemini API  
- **Vector Database:** ChromaDB  
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)  
- **Deployment:** Render  

---
## 📂 Project Structure
```
Healthibite-GenAI/
│
├── app.py
├── rag.py                  # Lightweight RAG (TF-IDF for deployment)
├── database.py
├── requirements.txt
│
├── templates/
├── static/
├── data/
│
└── advanced_rag/
    ├── rag_embedding.py    # Embedding-based RAG (SentenceTransformer + ChromaDB)
    ├── create_embeddings.py
    └── README.md
```
---
## 🧠 How It Works

1. **User Input**
   - Age
   - Goal (weight management, energy, sleep, etc.)
   - Activity level
   - Health-related query

2. **RAG Pipeline (Local Implementation)**
   - Query classification (health vs non-health)
   - Query embedding generation
   - Retrieval of relevant documents using vector similarity
   - Re-ranking using cosine similarity

3. **Generation**
   - Retrieved context is passed to the AI model
   - AI generates structured recommendations

4. **Output**
   - Diet suggestions  
   - Exercise recommendations  
   - Sleep improvements  

⚠️ **Note:**  
The full RAG pipeline (embeddings + vector search) is implemented locally.  
For deployment, a lightweight version is used to ensure faster startup and avoid resource constraints.

---

## 📸 Output Screenshots

### 🔹 Home Page
<img width="717" height="621" alt="image" src="https://github.com/user-attachments/assets/e7c64847-746f-46c2-ad63-a9860ee4bc05" />

### 🔹 AI Recommendations Output
<img width="801" height="641" alt="image" src="https://github.com/user-attachments/assets/fda1f546-495c-43c8-8888-02f68fcd1ea2" />

<img width="858" height="547" alt="image" src="https://github.com/user-attachments/assets/695d7b2f-41bb-42c6-9fce-08ea2b97c9b8" />

---

## ⚠️ Handling Edge Cases

- 🔄 API quota limits → displays "AI is busy" message  
- ❌ Non-health queries → rejected gracefully  
- ⚡ Empty responses → handled to avoid UI break  

---

## 🚀 Installation (Local Setup)

```bash
git clone https://github.com/Manisha1808/Healthibite-GenAI.git
cd GenAI-Healthibite
pip install -r requirements.txt

Create a .env file:

GEMINI_API_KEY=your_api_key_here

Run the application:

python app.py
```

## 📈 Future Improvements
🔄 Full RAG deployment with precomputed embeddings
📊 User history & tracking
📱 Mobile responsiveness improvements
🧬 Advanced personalization using user profiles
⚡ Faster inference with optimized pipelines

## 🙌 Acknowledgements
Google Gemini API
Sentence Transformers
ChromaDB
Open-source ML & Web frameworks

## 📬 Contact

Feel free to connect for feedback, collaboration, or opportunities!
