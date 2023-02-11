from flask import Flask, jsonify, request
from canvasapi import Canvas
import json
from datetime import datetime, timedelta

app = Flask(__name__)


@app.route("/")
def home():
    return "Hi"


@app.route("/api/v1/course")
def course():
    return "course"


@app.route("/api/v1/assignments")
def assignments():
    return "course"


@app.route("/api/v1/courses")
def courses():
    key = request.headers.get("Authorization", None)
    api = Canvas("https://canvas.instructure.com", str(key))
    user = api.get_current_user()
    course_list = user.get_courses(enrollment_state="active")
    res = []
    for c in course_list:
        obj = {"id": c.id, "name": c.name}
        res.append(obj)

    return jsonify(res)

@app.route("/api/v1/user/assignments")
def user_assignments():
    key = request.headers.get("Authorization", None)
    api = Canvas("https://canvas.instructure.com", str(key))
    user = api.get_current_user()
    # courses = user.get_courses(enrollment_state="active")
    courses = []
    with open("config.json", "r") as f:
        courses = json.load(f)
    f = open("data.json", "w")
    filtered = []
    for cobj in courses:
        cid = cobj['canvas_id']
        cname = cobj['name']
        tid = cobj['todoist_id']
        c = api.get_course(cid)
        assignments = c.get_assignments()
        for a in assignments:
            if a.due_at is None:
                continue
            if datetime.strptime(a.due_at, "%Y-%m-%dT%H:%M:%SZ") > datetime.now():
                due_obj = datetime.strptime(a.due_at, "%Y-%m-%dT%H:%M:%SZ")
                filtered.append({"course_id": str(cid), "todoist_id": tid, "course_name": cname, "name": a.name,
                                 "due_at": str(due_obj.strftime("%B %d, %Y %I:%M%p")), "id": a.id})
        # print(datetime.now() < datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))

    json.dump(filtered, f)
    f.close()
    return jsonify(filtered)

@app.route("/api/v1/course/<int:id>/assignments")
def course_assignments(id):
