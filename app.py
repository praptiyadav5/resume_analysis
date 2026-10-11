import os

from flask import Flask, render_template, request, redirect, session
from db import engine, SessionLocal
from db import Base
import model as model
import PyPDF2
import docx
import json
from ai import analyze_resume
from career_simulation import detect_level, career_paths, what_if_analysis

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

# Create tables on startup
Base.metadata.create_all(bind=engine)


@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        db = SessionLocal()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("signup.html", error="Email and password are required.")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters.")

        existing_user = db.query(model.User).filter_by(email=email).first()
        if existing_user:
            return render_template("signup.html", error="An account with this email already exists.")

        user = model.User(email=email, password=password)
        db.add(user)
        db.commit()
        db.close()
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = SessionLocal()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = db.query(model.User).filter_by(email=email, password=password).first()
        db.close()

        if user:
            session["user"] = user.email
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid email or password. Please try again.")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role", "").strip()
        resume_text = request.form.get("resume", "").strip()
        file = request.files.get("file")

        # Extract text from uploaded file
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Could not read PDF: {str(e)}"}

            elif file.filename.endswith(".docx"):
                try:
                    document = docx.Document(file)
                    text = ""
                    for para in document.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Could not read DOCX: {str(e)}"}
            else:
                result = {"error": "Unsupported file type. Please upload PDF or DOCX."}

        if not result:
            if not resume_text:
                result = {"error": "Please upload a file or paste your resume text."}
            elif not user_goal:
                result = {"error": "Please enter a target role."}
            else:
                try:
                    result = analyze_resume(resume_text, user_goal)

                    # Career simulation enrichment
                    level = detect_level(resume_text)
                    missing_lower = [s.lower() for s in result.get("missing_skills", [])]
                    current_path, improved_path = career_paths(resume_text, missing_lower)
                    result["career_level"] = level
                    result["current_path"] = current_path
                    result["improved_path"] = improved_path

                    # Save to DB
                    db = SessionLocal()
                    user = db.query(model.User).filter_by(email=session["user"]).first()
                    report = model.Report(
                        user_id=user.id,
                        resume_text=resume_text[:5000],
                        result=json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
                    db.close()

                except Exception as e:
                    result = {"error": f"AI analysis failed: {str(e)}"}

    return render_template("dashboard.html", user=session["user"], result=result)


@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    user = db.query(model.User).filter_by(email=session["user"]).first()
    raw_reports = db.query(model.Report).filter_by(user_id=user.id).order_by(model.Report.id.desc()).all()
    db.close()

    parsed_reports = []
    for r in raw_reports:
        try:
            parsed_result = json.loads(r.result)
        except Exception:
            parsed_result = {}
        parsed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    return render_template("history.html", reports=parsed_reports)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
