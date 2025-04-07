from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from data_preprocessor import load_and_clean

def build_index(df):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast & lightweight
    embeddings = model.encode(df['Text for Embedding'].tolist(), show_progress_bar=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, embeddings, model

def save_index(index, df, embeddings):
    faiss.write_index(index, 'shl_index.faiss')
    df.to_csv("shl_indexed_data.csv", index=False)
    np.save("embeddings.npy", embeddings)

if __name__ == "__main__":
    df = load_and_clean()
    index, embeddings, model = build_index(df)
    save_index(index, df, embeddings)
