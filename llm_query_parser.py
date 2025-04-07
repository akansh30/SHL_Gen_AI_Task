import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

def get_structured_prompt(user_query: str) -> str:
    return f"""
You are an intelligent assistant. Extract structured information from the following input.

Input: "{user_query}"

Return a valid JSON object with **only** these keys:
- skills: list of required skills (e.g. cognitive, Python)
- traits: job traits or behavioral traits (e.g. entry-level, leadership)
- duration_limit: number in minutes (e.g. 30, 45)
- remote: true/false depending on whether remote assessment is requested

Only output valid JSON. No code blocks. No explanation.
"""

def query_groq_llm(prompt: str) -> dict:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        # 🧼 Remove code block wrappers or explanation if present
        if content.startswith("```"):
            content = content.strip("`").strip()
            if content.startswith("json"):
                content = content[4:].strip()

        return json.loads(content)

    except json.JSONDecodeError as e:
        print("⚠️ JSON parsing failed:", e)
        print("📝 Raw content returned:", content)
        return {}

    except Exception as e:
        print("❌ Groq API error:", e)
        return {}
