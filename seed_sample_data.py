"""
seed_sample_data.py
Optional helper to populate the database with a small amount of
dummy/synthetic data so the application can be demonstrated and
screenshotted. Uses fictitious names only (no real student data).
Run this AFTER database.py has created the schema.
"""

from database import get_db

def seed():
    db = get_db()

    db.execute("INSERT INTO classes (class_name, section, session) VALUES ('X', 'A', '2026-2027')")
    db.execute("INSERT INTO classes (class_name, section, session) VALUES ('IX', 'A', '2026-2027')")
    class_x = db.execute("SELECT id FROM classes WHERE class_name='X'").fetchone()["id"]
    class_ix = db.execute("SELECT id FROM classes WHERE class_name='IX'").fetchone()["id"]

    students = [
        ("STU001", "Aarav Sharma", "2011-04-12", "Male", "9876543210", "Delhi", class_x),
        ("STU002", "Diya Verma", "2011-06-03", "Female", "9876543211", "Delhi", class_x),
        ("STU003", "Kabir Singh", "2012-01-20", "Male", "9876543212", "Delhi", class_ix),
    ]
    for s in students:
        db.execute(
            """INSERT INTO students (admission_no, name, dob, gender, phone, address, class_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            s,
        )

    for subj in ["Mathematics", "Science", "English"]:
        db.execute("INSERT INTO subjects (subject_name, code) VALUES (?, ?)", (subj, subj[:3].upper()))

    db.execute("INSERT INTO exams (exam_name, session) VALUES ('Half Yearly', '2026-2027')")

    db.commit()
    db.close()
    print("Sample data inserted.")


if __name__ == "__main__":
    seed()
