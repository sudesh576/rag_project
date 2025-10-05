# Simple LLM caller — replace with preferred model and client. Here we use OpenAI Chat Completions as example.
import os
import requests


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def call_llm(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 512,
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data['choices'][0]['message']['content']