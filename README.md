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
- Designed a **production-ready Flask application deployed on Render**  
- Optimized system for **low-latency and free-tier deployment constraints**

---
## ✨ Features

- 🧠 Full **RAG (Retrieval-Augmented Generation)** pipeline using embeddings
- 🔍 Semantic search over health dataset using vector similarity
- 📊 Re-ranking of retrieved documents for improved relevance
- 🤖 AI-generated personalized recommendations
- 🎯 Structured output (Diet, Exercise, Sleep)
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

Healthibite-GenAI/
│
├── app.py
├── rag.py
├── database.py
├── requirements.txt
│
├── templates/
├── static/
├── data/
│
└── advanced_rag/
├── create_embeddings.py
├── rag_embeddings.py

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
<img width="975" height="821" alt="image" src="https://github.com/user-attachments/assets/c2677d45-3c83-42c2-9042-175c81186f42" />

### 🔹 AI Recommendations Output
<img width="975" height="582" alt="image" src="https://github.com/user-attachments/assets/57704e4d-4640-4d20-9384-7e18da0e68e4" />

<img width="975" height="486" alt="image" src="https://github.com/user-attachments/assets/17a3f1a7-5fcc-4eb3-86b5-fae08180e845" />

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
