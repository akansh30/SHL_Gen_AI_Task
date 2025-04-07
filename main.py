import streamlit as st
import requests
import pandas as pd
import json

from llm_query_parser import get_structured_prompt, query_groq_llm

st.set_page_config(page_title="SHL Assessment Recommender", layout="wide")
st.title("🔍 SHL Assessment Recommender")
st.write("Enter a job description URL or natural language query to get relevant SHL assessments.")

# Input area
query = st.text_area("📄 Job Description / Query", height=200)
use_llm = st.checkbox("🤖 Use LLM for Smart Query Understanding", value=True)

if st.button("🚀 Get Recommendations"):
    if not query.strip():
        st.warning("Please enter a query before submitting.")
    else:
        with st.spinner("Getting recommendations..."):
            try:
                # Optionally enhance the query using LLM
                if use_llm:
                    structured = query_groq_llm(get_structured_prompt(query))

                    # Show LLM Parsed Result Nicely
                    st.subheader("🧠 LLM Parsed Query:")
                    st.json(structured)

                    # Construct enhanced query string
                    traits = ", ".join(structured.get("traits", []))
                    skills = ", ".join(structured.get("skills", []))
                    duration = structured.get("duration_limit", 60)
                    remote = "with remote support" if structured.get("remote", False) else "on-site"

                    enhanced_query = f"{traits} role needing assessments for {skills}, under {duration} minutes, {remote}."
                    payload = {"text": enhanced_query}
                else:
                    payload = {"text": query}

                # Call recommender API
                response = requests.post(
                    "https://shl-gen-ai-backend.onrender.com/recommend",
                    headers={"Content-Type": "application/json"},
                    json=payload
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df = pd.DataFrame(data)

                        # Link assessment names to their URLs
                        df["Assessment Name"] = df.apply(
                            lambda row: f"[{row['assessment_name']}]({row['url']})", axis=1
                        )

                        df = df.rename(columns={
                            "Assessment Name": "Assessment Name (Linked)",
                            "remote": "Remote Testing Support",
                            "adaptive": "Adaptive/IRT Support",
                            "duration": "Duration",
                            "test_type": "Test Type"
                        })

                        df = df[[
                            "Assessment Name (Linked)",
                            "Remote Testing Support",
                            "Adaptive/IRT Support",
                            "Duration",
                            "Test Type"
                        ]]

                        st.success(f"Showing top {len(df)} recommendations:")
                        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
                    else:
                        st.info("No relevant assessments found.")
                else:
                    st.error(f"API returned error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Error connecting to API: {e}")
