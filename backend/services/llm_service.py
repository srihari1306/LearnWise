# backend/services/llm_service.py
import os
import json
import numpy as np
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Text generation model
GEN_MODEL_NAME = "gemini-1.5-flash"   # or "gemini-1.5-pro" for better reasoning
gen_model = genai.GenerativeModel(GEN_MODEL_NAME)

def generate_study_package(raw_text: str, course_title: str, deadline: str = None):
    """
    Calls Gemini LLM once and returns a dict with:
    {
        "summary": str,
        "study_plan": dict,
        "videos": list[dict]
    }
    """
    deadline_text = deadline if deadline else "soon"

    prompt = f"""
You are an AI study assistant. A student uploaded a syllabus/content document. 
Your job is to return a JSON object with the following keys:

1. "summary": A concise but clear summary of the document (max 250 words).
2. "study_plan": A structured week-by-week or day-by-day plan to cover the material,
   considering the course title "{course_title}" and deadline "{deadline_text}".
   Keep it as a JSON object (keys = "week1", "week2", or "day1", "day2", etc.).
3. "videos": A list of 3-5 recommended YouTube videos (with `title` and `url` fields)
   that would help the student understand this subject. Use real, existing YouTube links
   that match the topic "{course_title}".

Document content (use it to inform summary, plan, and videos):

\"\"\"{raw_text[:6000]}\"\"\"   # trimmed for token safety

Return ONLY valid JSON in your final output, no explanations.
"""

    try:
        response = gen_model.generate_content(prompt)

        # Sometimes the response might contain markdown fences → clean it
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
        if text.startswith("json"):
            text = text[len("json"):].strip()

        data = json.loads(text)

        # normalize structure
        return {
            "summary": data.get("summary", ""),
            "study_plan": data.get("study_plan", {}),
            "videos": data.get("videos", []),
        }

    except Exception as e:
        print("Gemini error:", e)
        return {
            "summary": "Error generating summary",
            "study_plan": {},
            "videos": []
        }


# Embeddings (for semantic search)
def embed_text(text: str) -> list[float]:
    """Get embedding vector for a chunk of text using Gemini embeddings."""
    resp = genai.embed_content(
        model="models/embedding-001",  # correct embedding model ID
        content=text
    )
    return resp["embedding"]


def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


# Chat Q&A
def answer_question_with_context(question: str, context: str) -> str:
    """Answer a question using the provided context."""
    prompt = f"""
You are a helpful study assistant. 
Use the following syllabus/content as context to answer the user's question.

Context:
{context}

Question: {question}

Answer concisely. 
If the answer is not in the context, reply: "I don’t know from the material."
"""
    response = gen_model.generate_content(prompt)
    return response.text.strip()
