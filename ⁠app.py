from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


class StudentDatabase:

  def __init__(self):
    self.profile = {}
    self.subjects = []
    self.lessons = []
    self.errors = []
    self.tasks = []


db = StudentDatabase()


class AdaptiveAIPlanner:

  @staticmethod
  def calculate_priority(coefficient, difficulty, mastery):
    return (coefficient * 0.3) + (difficulty * 0.3) + ((100 - mastery) * 0.4)

  @staticmethod
  def generate_initial_plan(profile):
    db.subjects = [
        {"id": 1, "name": "الرياضيات", "coefficient": 5},
        {"id": 2, "name": "العلوم الطبيعية", "coefficient": 5},
        {"id": 3, "name": "الفيزياء", "coefficient": 4},
        {"id": 4, "name": "العربية والأدب", "coefficient": 3},
    ]

    db.lessons = [
        {
            "id": 1,
            "subject_id": 1,
            "name": "الدوال العددية",
            "difficulty": 9,
            "mastery": 30,
        },
        {
            "id": 2,
            "subject_id": 1,
            "name": "المتتاليات العددية",
            "difficulty": 8,
            "mastery": 50,
        },
        {
            "id": 3,
            "subject_id": 2,
            "name": "المناعة",
            "difficulty": 7,
            "mastery": 60,
        },
        {
            "id": 4,
            "subject_id": 3,
            "name": "الميكانيك",
            "difficulty": 9,
            "mastery": 40,
        },
    ]

    tasks = []
    for lesson in db.lessons:
      sub = next(s for s in db.subjects if s["id"] == lesson["subject_id"])
      priority = AdaptiveAIPlanner.calculate_priority(
          sub["coefficient"], lesson["difficulty"], lesson["mastery"]
      )
      tasks.append({
          "lesson": lesson["name"],
          "subject": sub["name"],
          "priority_score": round(priority, 2),
          "status": "مطلوب اليوم",
      })

    tasks.sort(key=lambda x: x["priority_score"], reverse=True)
    db.tasks = tasks


@app.route("/")
def home():
  if not db.profile:
    return render_template("index.html", step="onboarding")
  return render_template(
      "index.html",
      step="dashboard",
      profile=db.profile,
      tasks=db.tasks,
      errors=db.errors,
  )


@app.route("/submit_onboarding", methods=["POST"])
def submit_onboarding():
  data = request.form
  db.profile = {
      "name": data.get("name"),
      "stream": data.get("stream"),
      "target_score": data.get("target_score"),
      "study_hours": data.get("study_hours"),
      "streak": 1,
      "expected_average": 15.5,
  }
  AdaptiveAIPlanner.generate_initial_plan(db.profile)
  return jsonify({"status": "success", "redirect": "/"})


@app.route("/log_error", methods=["POST"])
def log_error():
  data = request.json
  error_entry = {
      "lesson": data.get("lesson"),
      "error_type": data.get("error_type"),
      "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
  }
  db.errors.append(error_entry)

  for lesson in db.lessons:
    if lesson["name"] == data.get("lesson"):
      lesson["mastery"] = max(0, lesson["mastery"] - 10)
  AdaptiveAIPlanner.generate_initial_plan(db.profile)

  return jsonify(
      {"status": "success", "message": "تم تسجيل الخطأ وتحديث الخطة بنجاح!"}
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8182, debug=True)
