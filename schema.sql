-- School Management & Student Information System
-- Database Schema (SQLite)

DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS fee_payments;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'teacher'))
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    section TEXT NOT NULL,
    session TEXT NOT NULL,
    UNIQUE(class_name, section, session)
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    dob TEXT,
    gender TEXT,
    phone TEXT,
    address TEXT,
    class_id INTEGER,
    FOREIGN KEY(class_id) REFERENCES classes(id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
    FOREIGN KEY(student_id) REFERENCES students(id),
    UNIQUE(student_id, attendance_date)
);

CREATE TABLE fee_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    fee_type TEXT NOT NULL,
    amount_due REAL NOT NULL,
    amount_paid REAL NOT NULL DEFAULT 0,
    payment_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
);

CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_name TEXT NOT NULL,
    code TEXT
);

CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_name TEXT NOT NULL,
    session TEXT NOT NULL
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    marks REAL NOT NULL CHECK(marks >= 0 AND marks <= 100),
    FOREIGN KEY(exam_id) REFERENCES exams(id),
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id),
    UNIQUE(exam_id, student_id, subject_id)
);
