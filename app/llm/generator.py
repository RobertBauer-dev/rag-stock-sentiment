"""
LLM response generator for stock sentiment analysis.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer_from_context(query: str, context_posts: List[Dict]) -> str:
    """
    Generate an answer to a question based on Reddit context posts.
    
    Args:
        query: The user's question
        context_posts: List of relevant Reddit posts as context
        
    Returns:
        Generated answer based on the context
    """
    context_text = "\n\n".join([
        f"{p['title']}\n{p.get('selftext', '')}" for p in context_posts
    ])

    prompt = f"""Du bist ein Finanzanalyst. Beantworte folgende Frage basierend auf Reddit-Posts:

Frage: {query}

Reddit-Kontext:
{context_text}

Antwort:"""

    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
