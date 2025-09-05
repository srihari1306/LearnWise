# backend/services/llm_service.py
import os
import json
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_NAME = "gemini-1.5-flash"  # use "gemini-1.5-pro" if you want better quality

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
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

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

def answer_question_with_context(question, chunks, top_k=3):
    # naive retrieval: keyword match scoring
    ranked = sorted(chunks, key=lambda c: question.lower() in c["text"].lower(), reverse=True)
    selected = ranked[:top_k]

    context = "\n\n".join([f"From {c['source']} (page {c['page']}):\n{c['text']}" for c in selected])

    prompt = f"""
You are a study assistant. 
Answer the student's question using the provided context from their PDFs.
Include clear explanations. 
If possible, cite which source/page you used.

Question: {question}

Context:
{context}
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    answer = response.text
    sources = [{"filename": c["source"], "page": c["page"]} for c in selected]

    return answer, sources