# TrekVerse - Trekking Management System
TrekVerse is a web-based Trekking Management System developed using Flask. It provides separate portals for Admin, Staff, and Users to efficiently manage trekking activities, bookings, and participant information.

## Features
### Admin
- Secure login
- Dashboard with trekking statistics
- Add, edit and delete treks
- Assign staff to treks
- Manage users and staff
- Approve staff registrations
- Blacklist/activate users
- View and manage bookings
- View trek history

### Staff
- Staff dashboard
- View assigned treks
- Manage trek participants
- Cancel participant bookings
- Update profile

### User
- Register and login
- Browse available treks
- Book treks
- Cancel bookings
- View booking history
- User dashboard

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- Jinja2

## Project Structure

```
Trekking_management/
│
├── app.py
├── config.py
├── models.py
├── routes.py
├── requirements.txt
├── trekking.db
├── static/
├── templates/
│   ├── admin/
│   ├── staff/
│   └── user/
└── README.md
```

## Installation

1. Clone the repository

```bash
git clone <repository-url>
```

2. Navigate to the project

```bash
cd Trekking_management
```

3. Create a virtual environment

```bash
python -m venv venv
```

4. Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

5. Install dependencies

```bash
pip install -r requirements.txt
```

6. Run the application

```bash
python app.py
```

The application will run at

```
http://127.0.0.1:5000
```

## Roles

- Admin
- Staff
- User

## Database

SQLite

Tables:
- Users
- Treks
- Bookings

## Author
Prakruthi N.