# School Management & Student Information System

## Screenshots

![Dashboard](screenshots/updated_dashboard.png)
![Student Management](screenshots/Testresults.png)

## Overview

This application provides a centralized platform for managing essential school operations, including:

- Student records
- Class and section management
- Attendance tracking
- Fee management
- Examination and result management
- Dashboard and academic reports

The system uses **Flask** for the web application, **SQLite** for data persistence, and **HTML, CSS, JavaScript, and Jinja2** for the user interface.

## How to run it on your own computer

1. **Install Python 3.10+** if you don't already have it (check with `python3 --version`).

2. **Open a terminal in this folder** (`school_management/`).

3. **Create and activate a virtual environment:**
   ```
   python3 -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Initialize the database** (creates `school.db` with tables and a default admin user):
   ```
   python database.py
   ```

6. **(Optional) Load sample/dummy data** for demonstration purposes:
   ```
   python seed_sample_data.py
   ```
   This adds a couple of fictitious students, classes, subjects and an exam
   — useful only for taking demo screenshots. You can skip this and enter
   your own data instead if you prefer.

7. **Run the application:**
   ```
   python app.py
   ```

8. **Open your browser** to `http://127.0.0.1:5050`

9. **Log in** with the default admin account:
   - Username: `admin`
   - Password: `admin123`

   Change this password (or create a new admin user directly in the
   database) before treating this as anything beyond an academic demo.

## Project structure

```
school_management/
├── app.py              # Flask routes and application logic
├── database.py         # DB connection + one-time schema initialization
├── schema.sql           # Table definitions
├── seed_sample_data.py # Optional dummy data for screenshots
├── requirements.txt
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── classes.html
│   ├── attendance.html
│   ├── fees.html
│   ├── exams.html
│   ├── subjects.html
│   ├── results.html
│   └── reports.html
└── static/
    ├── css/style.css
    └── js/app.js
```
## Security Note

This project is intended for academic and demonstration purposes.

Before deploying the application in a production environment, additional
security measures should be implemented, including secure secret-key
management, password hashing, authorization controls, input validation,
database security, and production server configuration.

The repository uses dummy/sample data for demonstration purposes.
