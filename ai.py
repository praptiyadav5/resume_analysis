import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).with_name(".ENV"))

client = OpenAI(
    api_key=os.environ["OPENAIKEY"],
    base_url="https://api.groq.com/openai/v1"
)

def analyze_resume(resume_text, role):
    prompt = f"""
    You are a strict hiring manager.

    Analyze this resume for role: {role}

    STRICT RULES:
    - Extract only relevant skills
    - Identify missing skills
    - Give roadmap
    - Provide interview questions
    - Give score out of 100

    Return ONLY valid JSON:
    {{
        "score": 0,
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": []
    }}

    Resume:
    {resume_text}
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  
            messages=[
                {"role": "system", "content": "You are a strict hiring manager."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        text = response.choices[0].message.content.strip()

        # 🔥 Extract JSON safely
        start = text.find("{")
        end = text.rfind("}") + 1

        return json.loads(text[start:end])

    except Exception as e:
        return {
            "score": 0,
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }