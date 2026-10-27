# CampusFix — Smart Campus Issue Reporting and Resolution System

## Project Overview
CampusFix is a web-based application that allows students to report campus issues and track their resolution. Administrators can assign issues to staff, and staff can update issue statuses.

## Features
- Student and staff registration and login
- Campus issue reporting
- Student-specific issue tracking
- Admin dashboard and staff assignment
- Staff dashboard and status updates
- Issue details and assigned staff information

## Technologies Used
- Frontend: HTML, CSS
- Backend: Python and Flask
- Database: SQLite
- Version Control: Git and GitHub
- CI/CD: Jenkins
- Containerization: Docker

## Project Structure
- `backend/app.py` — Flask application and backend routes
- `index.html` — Login page
- `register.html` — Registration page
- `student-dashboard.html` — Student dashboard
- `admin-dashboard.html` — Admin dashboard
- `staff-dashboard.html` — Staff dashboard
- `style.css` — Application styling

## Run Locally
1. Install Python 3.11 or later.
2. Open a terminal in the `backend` directory.
3. Create and activate a Python virtual environment.
4. Install Flask using `pip install flask`.
5. Run `python app.py`.
6. Open the local URL displayed in the terminal.

## Testing
The student issue reporting, administrator assignment, staff status update, and student status tracking workflow has been tested.

## Future Work
- Automated testing through Jenkins
- Docker-based application deployment
