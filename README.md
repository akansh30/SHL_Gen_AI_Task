# SHL Gen AI Assessment Recommender

An intelligent recommendation system that takes a natural language job description or query and returns the most relevant SHL assessments using LLM-powered parsing, semantic search, and post-filtering logic.

---

## 🚀 Features

- ✅ Natural language input (job descriptions or queries)
- 🤖 LLM-enhanced query understanding using Groq (LLaMA 3.3 70B)
- 🔍 Semantic search with SentenceTransformers + FAISS
- 🎯 Structured post-filtering based on duration, remote support, deduplication
- 🖥️ FastAPI backend + Streamlit frontend
- ☁️ Deployed on Streamlit Cloud and Render

---

## 📸 Demo Screenshots

![Screenshot 2025-04-07 103030](https://github.com/user-attachments/assets/479333ec-8e4d-4191-8cca-a563fa99b5c1)
![Screenshot 2025-04-07 103036](https://github.com/user-attachments/assets/bed51294-3026-4f68-98fa-6291430c72ca)
![Screenshot 2025-04-07 103528](https://github.com/user-attachments/assets/fe43156e-b57e-44be-99a4-2309455e29c8)
![Screenshot 2025-04-07 103542](https://github.com/user-attachments/assets/e87993ba-5613-4be8-865a-86a9352a01e4)
![Screenshot 2025-04-07 103011](https://github.com/user-attachments/assets/3d0ba9e6-01bd-4485-8469-02e818cba348)
![Screenshot 2025-04-07 101426](https://github.com/user-attachments/assets/1f2edce9-dafd-4df6-8be3-c43a39c6746a)

---

## 🧠 Approach

### 1. Data Extraction
- Scraped SHL's assessment catalog using `scraper_shl.py` with Selenium + BeautifulSoup.
- Structured metadata into `shl_assessments_with_ids.csv`.

### 2. Embedding + Indexing
- Encoded assessment data using `SentenceTransformer ('all-MiniLM-L6-v2')`
- Built FAISS vector index using `embedding_index.py` → `shl_index.faiss`

### 3. LLM Query Parsing
- Parsed traits, skills, duration, remote requirement via `llm_query_parser.py`
- LLM used: Groq API with LLaMA 3.3 70B Versatile

### 4. Recommendation Logic
- Main logic inside `main.py` and `recommender_api.py`
- Steps:
  - Parse query (LLM)
  - Semantic search (FAISS)
  - Post-filter (duration, remote, duplicates)

### 5. Interfaces
- **API**: FastAPI (`/recommend`) in `recommender_api.py`
- **Frontend**: Streamlit UI (`main.py`)

---

## 🛠️ Tech Stack

| Category        | Tools / Libraries                      |
|-----------------|-----------------------------------------|
| Scraping        | Selenium, BeautifulSoup                |
| Embedding       | SentenceTransformers, FAISS            |
| LLM Parsing     | Groq API (LLaMA 3.3 70B Versatile)     |
| Backend         | FastAPI                                |
| Frontend        | Streamlit                              |
| Deployment      | Render, Streamlit Cloud                |
| Others          | Pandas, difflib, Pydantic              |

---

## 📁 Project Structure

```bash
├── data_preprocessor.py         # Preprocess scraped data
├── scraper_shl.py              # Scraper for SHL catalog
├── embedding_index.py          # Create embeddings + FAISS index
├── build_faiss_index.py        # CLI wrapper for building index
├── shl_assessments_with_ids.csv
├── shl_index.faiss             # Vector index for search
├── llm_query_parser.py         # Structured query generation using Groq LLM
├── recommender_api.py          # FastAPI backend
├── main.py                     # Streamlit frontend
├── requirements.txt
├── .gitignore
└── build.sh                    # Build script for deployment
``` 
## 🌐 Live Links

- **Streamlit Frontend:** https://shl-gen-ai.streamlit.app  
- **FastAPI Backend:** https://shl-gen-ai-backend.onrender.com/recommend  
- **GitHub Repository:** https://github.com/akansh30/SHL_Gen_AI_Task

> **Note:** Open the API URL once before using the Streamlit app to avoid cold-start delay.



## 📦 How to Run Locally

### 1. Clone Repo
```bash
git clone https://github.com/akansh30/SHL_Gen_AI_Task
cd SHL_Gen_AI_Task
```
## 📦 How to Run Locally

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Run Backend (FastAPI)
```bash
uvicorn recommender_api:app --reload
```
### 4. Run Frontend (Streamlit)
```bash
streamlit run main.py
```



