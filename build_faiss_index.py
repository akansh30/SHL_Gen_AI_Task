# build_faiss_index.py
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load your CSV
df = pd.read_csv("shl_assessments_full.csv")  # use your actual CSV filename

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define the column you want to embed
texts = df["Description"].fillna("").tolist()

# Create embeddings
embeddings = model.encode(texts, show_progress_bar=True)

# Convert to FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# Save index
faiss.write_index(index, "shl_index.faiss")

# Optional: Save metadata so you can access the DataFrame by ID later
df.to_csv("shl_assessments_with_ids.csv", index=False)
