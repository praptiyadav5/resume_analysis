def detect_level(text):
    text = text.lower()

    if "intern" in text or "fresher" in text:
        return "Beginner"
    elif "project" in text or "experience" in text:
        return "Intermediate"
    else:
        return "Advanced"


def career_paths(text, missing_skills):
    text = text.lower()

    # Default current path
    current = {
        "role": "Junior Developer",
        "salary": "₹4–6 LPA",
        "time": "0-6 months"
    }

    improved = {}

    # Logic for improved future
    if "machine learning" in missing_skills:
        improved = {
            "role": "Data Scientist",
            "salary": "₹10–18 LPA",
            "time": "6–8 months"
        }
    elif "sql" in missing_skills:
        improved = {
            "role": "Backend Developer",
            "salary": "₹8–12 LPA",
            "time": "3–5 months"
        }
    elif "python" in missing_skills:
        improved = {
            "role": "Python Developer",
            "salary": "₹6–10 LPA",
            "time": "2–4 months"
        }
    else:
        improved = {
            "role": "Software Engineer",
            "salary": "₹12–20 LPA",
            "time": "6–12 months"
        }

    return current, improved


def what_if_analysis(skill):
    skill = skill.lower()

    if skill == "python":
        return "If you learn Python → You can move into Software Development roles quickly."
    elif skill == "machine learning":
        return "If you learn ML → You can become a Data Scientist with high salary growth."
    elif skill == "sql":
        return "If you learn SQL → You can enter Backend or Data roles easily."
    else:
        return "This skill will improve your career opportunities."