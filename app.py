"""
app.py
School Management & Student Information System
Main Flask application: routes, validation and session handling.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime

from database import get_db, init_db, DB_PATH
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SMS_SECRET_KEY", "dev-secret-change-in-production")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@app.route("/")
@login_required
def dashboard():
    db = get_db()
    total_students = db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    total_classes = db.execute("SELECT COUNT(*) c FROM classes").fetchone()["c"]

    today = datetime.date.today().isoformat()
    present_today = db.execute(
        "SELECT COUNT(*) c FROM attendance WHERE attendance_date = ? AND status = 'Present'",
        (today,),
    ).fetchone()["c"]

    pending_fees = db.execute(
        "SELECT COALESCE(SUM(amount_due - amount_paid), 0) p FROM fee_payments"
    ).fetchone()["p"]

    recent_results = db.execute(
        """SELECT r.id, s.name student_name, sub.subject_name, r.marks, e.exam_name
           FROM results r
           JOIN students s ON s.id = r.student_id
           JOIN subjects sub ON sub.id = r.subject_id
           JOIN exams e ON e.id = r.exam_id
           ORDER BY r.id DESC LIMIT 5"""
    ).fetchall()
    db.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_classes=total_classes,
        present_today=present_today,
        pending_fees=pending_fees,
        today=today,
        recent_results=recent_results,
    )


# ---------------------------------------------------------------------------
# Class management
# ---------------------------------------------------------------------------
@app.route("/classes", methods=["GET", "POST"])
@login_required
def classes():
    db = get_db()
    if request.method == "POST":
        class_name = request.form.get("class_name", "").strip()
        section = request.form.get("section", "").strip()
        session_year = request.form.get("session", "").strip()
        if not class_name or not section or not session_year:
            flash("All class fields are required.", "error")
        else:
            try:
                db.execute(
                    "INSERT INTO classes (class_name, section, session) VALUES (?, ?, ?)",
                    (class_name, section, session_year),
                )
                db.commit()
                flash("Class added.", "success")
            except Exception:
                flash("This class/section already exists for the session.", "error")
        return redirect(url_for("classes"))

    rows = db.execute("SELECT * FROM classes ORDER BY class_name, section").fetchall()
    db.close()
    return render_template("classes.html", classes=rows)


# ---------------------------------------------------------------------------
# Student management
# ---------------------------------------------------------------------------
@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    db = get_db()

    if request.method == "POST":
        admission_no = request.form.get("admission_no", "").strip()
        name = request.form.get("name", "").strip()
        dob = request.form.get("dob", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        class_id = request.form.get("class_id") or None

        errors = []
        if not admission_no:
            errors.append("Admission number is required.")
        if not name:
            errors.append("Student name is required.")
        if phone and (not phone.isdigit() or len(phone) != 10):
            errors.append("Phone number must be exactly 10 digits.")

        if errors:
            for e in errors:
                flash(e, "error")
        else:
            try:
                db.execute(
                    """INSERT INTO students
                       (admission_no, name, dob, gender, phone, address, class_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (admission_no, name, dob, gender, phone, address, class_id),
                )
                db.commit()
                flash("Student added successfully.", "success")
            except Exception:
                flash("Admission number already exists.", "error")
        return redirect(url_for("students"))

    search = request.args.get("q", "").strip()
    if search:
        rows = db.execute(
            """SELECT st.*, c.class_name, c.section FROM students st
               LEFT JOIN classes c ON c.id = st.class_id
               WHERE st.name LIKE ? OR st.admission_no LIKE ?
               ORDER BY st.name""",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT st.*, c.class_name, c.section FROM students st
               LEFT JOIN classes c ON c.id = st.class_id
               ORDER BY st.name"""
        ).fetchall()

    class_list = db.execute("SELECT * FROM classes ORDER BY class_name, section").fetchall()
    db.close()
    return render_template("students.html", students=rows, classes=class_list, search=search)


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    db.close()
    flash("Student record deleted.", "success")
    return redirect(url_for("students"))


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
@app.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    db = get_db()

    if request.method == "POST":
        attendance_date = request.form.get("attendance_date")
        student_ids = request.form.getlist("student_id")
        for sid in student_ids:
            status = request.form.get(f"status_{sid}", "Present")
            db.execute(
                """INSERT INTO attendance (student_id, attendance_date, status)
                   VALUES (?, ?, ?)
                   ON CONFLICT(student_id, attendance_date)
                   DO UPDATE SET status = excluded.status""",
                (sid, attendance_date, status),
            )
        db.commit()
        flash("Attendance saved.", "success")
        return redirect(url_for("attendance", class_id=request.form.get("class_id"),
                                 attendance_date=attendance_date))

    class_id = request.args.get("class_id")
    attendance_date = request.args.get("attendance_date", datetime.date.today().isoformat())
    class_list = db.execute("SELECT * FROM classes ORDER BY class_name, section").fetchall()

    roster = []
    if class_id:
        roster = db.execute(
            """SELECT s.id, s.name, s.admission_no,
                      (SELECT status FROM attendance a
                       WHERE a.student_id = s.id AND a.attendance_date = ?) AS status
               FROM students s WHERE s.class_id = ? ORDER BY s.name""",
            (attendance_date, class_id),
        ).fetchall()
    db.close()
    return render_template(
        "attendance.html",
        classes=class_list,
        roster=roster,
        class_id=class_id,
        attendance_date=attendance_date,
    )


# ---------------------------------------------------------------------------
# Fees
# ---------------------------------------------------------------------------
@app.route("/fees", methods=["GET", "POST"])
@login_required
def fees():
    db = get_db()
    if request.method == "POST":
        student_id = request.form.get("student_id")
        fee_type = request.form.get("fee_type", "").strip()
        amount_due = request.form.get("amount_due", "0")
        amount_paid = request.form.get("amount_paid", "0")
        payment_date = request.form.get("payment_date")

        try:
            amount_due_f = float(amount_due)
            amount_paid_f = float(amount_paid)
            if amount_due_f < 0 or amount_paid_f < 0:
                raise ValueError
        except ValueError:
            flash("Fee amounts must be valid non-negative numbers.", "error")
            return redirect(url_for("fees"))

        db.execute(
            """INSERT INTO fee_payments (student_id, fee_type, amount_due, amount_paid, payment_date)
               VALUES (?, ?, ?, ?, ?)""",
            (student_id, fee_type, amount_due_f, amount_paid_f, payment_date),
        )
        db.commit()
        flash("Fee record saved.", "success")
        return redirect(url_for("fees"))

    rows = db.execute(
        """SELECT f.*, s.name student_name, s.admission_no
           FROM fee_payments f JOIN students s ON s.id = f.student_id
           ORDER BY f.id DESC"""
    ).fetchall()
    student_list = db.execute("SELECT id, name, admission_no FROM students ORDER BY name").fetchall()
    db.close()
    return render_template("fees.html", fees=rows, students=student_list)


# ---------------------------------------------------------------------------
# Examinations & Results
# ---------------------------------------------------------------------------
@app.route("/exams", methods=["GET", "POST"])
@login_required
def exams():
    db = get_db()
    if request.method == "POST":
        exam_name = request.form.get("exam_name", "").strip()
        session_year = request.form.get("session", "").strip()
        if exam_name and session_year:
            db.execute(
                "INSERT INTO exams (exam_name, session) VALUES (?, ?)",
                (exam_name, session_year),
            )
            db.commit()
            flash("Examination created.", "success")
        else:
            flash("Exam name and session are required.", "error")
        return redirect(url_for("exams"))

    rows = db.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
    db.close()
    return render_template("exams.html", exams=rows)


@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    db = get_db()
    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        student_id = request.form.get("student_id")
        subject_id = request.form.get("subject_id")
        marks = request.form.get("marks")

        try:
            marks_f = float(marks)
            if not (0 <= marks_f <= 100):
                raise ValueError
        except (ValueError, TypeError):
            flash("Marks must be a number between 0 and 100.", "error")
            return redirect(url_for("results"))

        try:
            db.execute(
                """INSERT INTO results (exam_id, student_id, subject_id, marks)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(exam_id, student_id, subject_id)
                   DO UPDATE SET marks = excluded.marks""",
                (exam_id, student_id, subject_id, marks_f),
            )
            db.commit()
            flash("Result saved.", "success")
        except Exception:
            flash("Could not save result.", "error")
        return redirect(url_for("results"))

    exam_list = db.execute("SELECT * FROM exams ORDER BY id DESC").fetchall()
    student_list = db.execute("SELECT id, name, admission_no FROM students ORDER BY name").fetchall()
    subject_list = db.execute("SELECT * FROM subjects ORDER BY subject_name").fetchall()
    result_rows = db.execute(
        """SELECT r.*, s.name student_name, sub.subject_name, e.exam_name
           FROM results r
           JOIN students s ON s.id = r.student_id
           JOIN subjects sub ON sub.id = r.subject_id
           JOIN exams e ON e.id = r.exam_id
           ORDER BY r.id DESC"""
    ).fetchall()
    db.close()
    return render_template(
        "results.html",
        exams=exam_list,
        students=student_list,
        subjects=subject_list,
        results=result_rows,
    )


@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():
    db = get_db()
    if request.method == "POST":
        subject_name = request.form.get("subject_name", "").strip()
        code = request.form.get("code", "").strip()
        if subject_name:
            db.execute(
                "INSERT INTO subjects (subject_name, code) VALUES (?, ?)",
                (subject_name, code),
            )
            db.commit()
            flash("Subject added.", "success")
        return redirect(url_for("subjects"))
    rows = db.execute("SELECT * FROM subjects ORDER BY subject_name").fetchall()
    db.close()
    return render_template("subjects.html", subjects=rows)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@app.route("/reports")
@login_required
def reports():
    db = get_db()
    attendance_summary = db.execute(
        """SELECT s.name, s.admission_no,
                  SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) present_days,
                  COUNT(a.id) total_days
           FROM students s LEFT JOIN attendance a ON a.student_id = s.id
           GROUP BY s.id ORDER BY s.name"""
    ).fetchall()

    fee_summary = db.execute(
        """SELECT s.name, s.admission_no,
                  COALESCE(SUM(f.amount_due), 0) total_due,
                  COALESCE(SUM(f.amount_paid), 0) total_paid
           FROM students s LEFT JOIN fee_payments f ON f.student_id = s.id
           GROUP BY s.id ORDER BY s.name"""
    ).fetchall()
    db.close()
    return render_template("reports.html", attendance_summary=attendance_summary, fee_summary=fee_summary)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=False, host="0.0.0.0", port=5050)
