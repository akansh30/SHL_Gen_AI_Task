from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
import difflib
# from llm_query_parser import get_structured_prompt, query_groq_llm  # Disable if using dummy
import traceback

# Initialize app
app = FastAPI()

# Enable CORS for frontend access (like Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE_DIR, "shl_index.faiss")
CSV_PATH = os.path.join(BASE_DIR, "shl_assessments_with_ids.csv")

# HuggingFace cache fix for Render
os.environ["TRANSFORMERS_CACHE"] = "./hf_cache"

# Load model and data
print("Loading FAISS index from:", INDEX_PATH)
print("Loading CSV from:", CSV_PATH)

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index(INDEX_PATH)
df = pd.read_csv(CSV_PATH)

# Pydantic Schemas
class Query(BaseModel):
    text: str

class AssessmentOut(BaseModel):
    assessment_name: str
    url: str
    remote: str
    adaptive: str
    duration: str
    test_type: str

# Healthcheck
@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)  # ✅ Fixes 405 on Render health check
def home():
    return {"message": "SHL Recommender API is running"}

# Main recommendation endpoint
@app.post("/recommend", response_model=List[AssessmentOut])
def recommend(query: Query):
    print("Received query:", query.text)

    # Step 1: Parse with LLM (or dummy for now)
    try:
        # prompt = get_structured_prompt(query.text)
        # parsed = query_groq_llm(prompt)  # ❌ Temporarily comment this out

        # ✅ Dummy parsed data for testing without LLM
        parsed = {
            "skills": ["communication", "project management"],
            "traits": ["client-facing"],
            "duration_limit": 50,
            "remote": False
        }
        print("LLM Parsed (Dummy):", parsed)
    except Exception as e:
        print("LLM ERROR:", str(e))
        traceback.print_exc()
        parsed = {
            "skills": [],
            "traits": [],
            "duration_limit": None,
            "remote": None
        }

    skills = parsed.get("skills", [])
    traits = parsed.get("traits", [])
    duration_limit = parsed.get("duration_limit", None)
    remote_required = parsed.get("remote", None)

    # Step 2: Build enhanced query
    enhanced_query = f"A {' and '.join(traits)} role needing {' and '.join(skills)} assessments"
    if duration_limit:
        enhanced_query += f" under {duration_limit} minutes"
    if remote_required:
        enhanced_query += " with remote testing"

    print("Enhanced Query:", enhanced_query)

    # Step 3: FAISS vector search
    vector = model.encode([enhanced_query])
    top_k = min(200, index.ntotal)
    D, I = index.search(vector, top_k)

    # Step 4: Post-filter results
    seen_names = []
    results = []

    for idx in I[0]:
        row = df.iloc[idx]
        name = row.get("Assessment Name", "")
        url = str(row.get("URL", ""))

        if any(difflib.SequenceMatcher(None, name, existing).ratio() > 0.9 for existing in seen_names):
            continue

        duration = row.get("Assessment Length", None)
        is_remote = row.get("Remote", False)

        if duration_limit and pd.notna(duration):
            try:
                if int(duration) > int(duration_limit):
                    continue
            except:
                pass

        if remote_required is not None and bool(is_remote) != bool(remote_required):
            continue

        seen_names.append(name)

        results.append(AssessmentOut(
            assessment_name=name,
            url=url,
            remote="Yes" if is_remote else "No",
            adaptive="Yes" if row.get("Adaptive", False) else "No",
            duration=str(duration) if pd.notna(duration) else "Unknown",
            test_type=str(row.get("Test Types", "")) if pd.notna(row.get("Test Types", "")) else "Unknown"
        ))

        if len(results) >= 10:
            break

    return results
