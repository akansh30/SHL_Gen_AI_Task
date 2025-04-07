import pandas as pd
import re

def preprocess(text):
    if pd.isna(text):
        return ""
    text = re.sub(r'\s+', ' ', text)  # Remove excess whitespace
    return text.strip().lower()

def load_and_clean(path='shl_assessments_full.csv'):
    df = pd.read_csv(path)
    df['Cleaned Description'] = df['Description'].apply(preprocess)
    df['Text for Embedding'] = df.apply(
        lambda row: f"{row['Assessment Name']}. {row['Cleaned Description']}. Duration: {row['Duration']} mins. Test Type: {row['Test Type']}", axis=1
    )
    return df
