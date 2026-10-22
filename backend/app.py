import os
import sqlite3
from flask import Flask, request, session, send_from_directory

app = Flask(__name__)

app.secret_key = "campusfix-secret-key"

# Location of the database
DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "campusfix.db"
)

# Location of the frontend files
FRONTEND_FOLDER = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "department" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")

    # USERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT
        )
    """)

    # ISSUES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            reported_date TEXT NOT NULL,
            reported_by INTEGER,
            FOREIGN KEY (reported_by) REFERENCES users(id)
        )
    """)

    # ASSIGNMENTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            assigned_date TEXT NOT NULL,
            FOREIGN KEY (issue_id) REFERENCES issues(id),
            FOREIGN KEY (staff_id) REFERENCES users(id)
        )
    """)

    # STATUS UPDATES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            remarks TEXT,
            updated_date TEXT NOT NULL,
            FOREIGN KEY (issue_id) REFERENCES issues(id)
        )
    """)

    # --------------------------------------------------
    # CREATE STAFF USERS IF THEY DON'T EXIST
    # --------------------------------------------------

    staff_users = [
        ("Arun", "arun@campusfix.com", "arun123", "Staff"),
        ("Priya", "priya@campusfix.com", "priya123", "Staff"),
        ("Rahul", "rahul@campusfix.com", "rahul123", "Staff"),
        ("Meena", "meena@campusfix.com", "meena123", "Staff")
    ]

    for name, email, password, role in staff_users:

        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user is None:

            cursor.execute("""
                INSERT INTO users
                (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                password,
                role
            ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


# --------------------------------------------------
# TEST ROUTE
# --------------------------------------------------

@app.route("/add-test-user")
def add_test_user():

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO users
            (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Test User",
            "test@campusfix.com",
            "1234",
            "Student"
        ))

        conn.commit()

        message = "Test user added successfully!"

    except sqlite3.IntegrityError:

        message = "Test user already exists."

    conn.close()

    return message


# --------------------------------------------------
# REGISTER
# --------------------------------------------------


@app.route("/register", methods=["POST"])
def register():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""
    role = (request.form.get("role") or "").strip().title()
    department = (request.form.get("department") or "").strip()

    if not name or not email or not password:
        return "Please fill in all required fields."

    if password != confirm_password:
        return "Passwords do not match."

    if role not in ("Student", "Staff"):
        return "Please select Student or Staff."

    if role == "Student":
        if not email.endswith("student@campusfix.com"):
            return "Student email must end with student@campusfix.com."
        department = None

    elif role == "Staff":
        if not email.endswith("staff@campusfix.com"):
            return "Staff email must end with staff@campusfix.com."
        if not department:
            return "Please select your department."

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO users (name, email, password, role, department)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, password, role, department))

        conn.commit()
        return "Registration successful! You can now log in."

    except sqlite3.IntegrityError:
        return "This email is already registered. Please use a different email."

    finally:
        conn.close()



# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db()

    user = conn.execute("""
        SELECT id, name, email, password, role
        FROM users
        WHERE email = ? AND password = ?
    """, (
        email,
        password
    )).fetchone()

    conn.close()

    if user is None:
        return "Invalid email or password."

    # Store login information in Flask session
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["role"] = user["role"]

    if user["role"] == "Staff":
        return "Staff login successful!"

    elif user["role"] == "Admin":
        return "Admin login successful!"

    elif user["role"] == "Student":
        return "Student login successful!"

    return "Login successful!"


# --------------------------------------------------
# REPORT ISSUE
# --------------------------------------------------

@app.route("/report-issue", methods=["POST"])
def report_issue():

    title = request.form.get("title")
    category = request.form.get("category")
    location = request.form.get("location")
    description = request.form.get("description")
    priority = request.form.get("priority")

    reported_date = __import__("datetime").datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    reported_by = session.get("user_id")

    conn = get_db()

    conn.execute("""
        INSERT INTO issues
        (
            title,
            category,
            location,
            description,
            priority,
            status,
            reported_date,
            reported_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        category,
        location,
        description,
        priority,
        "Pending",
        reported_date,
        reported_by
    ))

    conn.commit()
    conn.close()

    return "Issue reported successfully!"


# --------------------------------------------------
# ADMIN - VIEW ALL ISSUES
# --------------------------------------------------


@app.route("/admin-issues")
def admin_issues():

    conn = get_db()

    issues = conn.execute("""
        SELECT
            issues.id,
            issues.title,
            issues.category,
            issues.location,
            issues.description,
            issues.priority,
            issues.status,
            issues.reported_date,
            users.name AS reporter_name,
            users.email AS reporter_email,
            staff.name AS staff_name,
            staff.email AS staff_email,
            staff.department AS staff_department
        FROM issues
        LEFT JOIN users
            ON issues.reported_by = users.id
        LEFT JOIN assignments
            ON issues.id = assignments.issue_id
        LEFT JOIN users AS staff
            ON assignments.staff_id = staff.id
        ORDER BY issues.id DESC
    """).fetchall()

    conn.close()

    return {
        "issues": [dict(issue) for issue in issues]
    }



# --------------------------------------------------
# ASSIGN STAFF
# --------------------------------------------------

@app.route("/assign-staff", methods=["POST"])
def assign_staff():

    issue_id = request.form.get("issue_id")
    staff_id = request.form.get("staff_id")

    assigned_date = __import__("datetime").datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = get_db()

    # Check whether assignment already exists
    existing_assignment = conn.execute("""
        SELECT id
        FROM assignments
        WHERE issue_id = ?
    """, (
        issue_id,
    )).fetchone()

    if existing_assignment:

        conn.execute("""
            UPDATE assignments
            SET staff_id = ?,
                assigned_date = ?
            WHERE issue_id = ?
        """, (
            staff_id,
            assigned_date,
            issue_id
        ))

    else:

        conn.execute("""
            INSERT INTO assignments
            (
                issue_id,
                staff_id,
                assigned_date
            )
            VALUES (?, ?, ?)
        """, (
            issue_id,
            staff_id,
            assigned_date
        ))

    # Change issue status to Assigned
    conn.execute("""
        UPDATE issues
        SET status = ?
        WHERE id = ?
    """, (
        "Assigned",
        issue_id
    ))

    conn.commit()
    conn.close()

    return "Staff assigned successfully!"


# --------------------------------------------------
# STAFF - VIEW THEIR ASSIGNED ISSUES
# --------------------------------------------------


@app.route("/staff-issues")
def staff_issues():

    if "user_id" not in session:
        return {
            "error": "Please login first."
        }, 401

    if session.get("role") != "Staff":
        return {
            "error": "Access denied."
        }, 403

    staff_id = session["user_id"]

    conn = get_db()

    issues = conn.execute("""
        SELECT
            issues.id,
            issues.title,
            issues.category,
            issues.location,
            issues.description,
            issues.priority,
            issues.status,
            issues.reported_date,
            users.name AS reporter_name,
            users.email AS reporter_email
        FROM issues
        INNER JOIN assignments
            ON issues.id = assignments.issue_id
        LEFT JOIN users
            ON issues.reported_by = users.id
        WHERE assignments.staff_id = ?
        ORDER BY issues.id DESC
    """, (staff_id,)).fetchall()

    conn.close()

    return {
        "staff_id": staff_id,
        "staff_name": session.get("user_name"),
        "issues": [dict(issue) for issue in issues]
    }



@app.route("/staff-users")
def staff_users():

    if "user_id" not in session:
        return {"error": "Please login first."}, 401

    if session.get("role") != "Admin":
        return {"error": "Access denied."}, 403

    conn = get_db()

    staff = conn.execute("""
        SELECT id, name, department
        FROM users
        WHERE role = 'Staff'
        ORDER BY name
    """).fetchall()

    conn.close()

    return {
        "staff": [dict(member) for member in staff]
    }


# --------------------------------------------------
# UPDATE ISSUE STATUS
# --------------------------------------------------

@app.route("/update-status", methods=["POST"])
def update_status():

    issue_id = request.form.get("issue_id")
    status = request.form.get("status")
    remarks = request.form.get("remarks")

    updated_date = __import__("datetime").datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = get_db()

    # Update current status
    conn.execute("""
        UPDATE issues
        SET status = ?
        WHERE id = ?
    """, (
        status,
        issue_id
    ))

    # Save status history
    conn.execute("""
        INSERT INTO status_updates
        (
            issue_id,
            status,
            remarks,
            updated_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        issue_id,
        status,
        remarks,
        updated_date
    ))

    conn.commit()
    conn.close()

    return "Issue status updated successfully!"


# --------------------------------------------------
# STUDENT - VIEW MY ISSUES
# --------------------------------------------------



@app.route("/my-issues")
def my_issues():

    if "user_id" not in session:
        return {"error": "Please login first."}, 401

    if session.get("role") != "Student":
        return {"error": "Access denied."}, 403

    student_id = session["user_id"]

    conn = get_db()

    issues = conn.execute("""
        SELECT
            issues.id,
            issues.title,
            issues.category,
            issues.location,
            issues.description,
            issues.priority,
            issues.status,
            issues.reported_date,
            staff.name AS staff_name,
            staff.email AS staff_email,
            staff.department AS staff_department
        FROM issues
        LEFT JOIN assignments
            ON issues.id = assignments.issue_id
        LEFT JOIN users AS staff
            ON assignments.staff_id = staff.id
        WHERE issues.reported_by = ?
        ORDER BY issues.id DESC
    """, (student_id,)).fetchall()

    conn.close()

    return {
        "student_id": student_id,
        "student_name": session.get("user_name"),
        "issues": [dict(issue) for issue in issues]
    }




# --------------------------------------------------
# ISSUE DETAILS
# --------------------------------------------------


@app.route("/issue/<int:issue_id>")
def issue_details(issue_id):

    if "user_id" not in session:
        return {
            "error": "Please login first."
        }, 401

    if session.get("role") != "Student":
        return {
            "error": "Access denied."
        }, 403

    student_id = session["user_id"]

    conn = get_db()

    issue = conn.execute("""
        SELECT
            issues.id,
            issues.title,
            issues.category,
            issues.location,
            issues.description,
            issues.priority,
            issues.status,
            issues.reported_date,
            staff.name AS staff_name,
            staff.email AS staff_email,
            staff.department AS staff_department
        FROM issues
        LEFT JOIN assignments
            ON issues.id = assignments.issue_id
        LEFT JOIN users AS staff
            ON assignments.staff_id = staff.id
        WHERE issues.id = ?
          AND issues.reported_by = ?
    """, (issue_id, student_id)).fetchone()

    conn.close()

    if issue is None:
        return {
            "error": "Issue not found."
        }, 404

    return dict(issue)



# --------------------------------------------------
# SERVE FRONTEND FILES
# --------------------------------------------------

@app.route("/<path:filename>")
def serve_frontend(filename):

    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)