# Task Management API

A robust and clean Task Management REST API built with Django and Django REST Framework (DRF). This project is part of the ALX Backend Capstone - Part 3 implementation.

## 🚀 Features (Part 3 Implementation)
- **User-Based Task Isolation**: Users can only create, view, update, and delete their own tasks.
- **Full CRUD Support**: Manage tasks with titles, descriptions, due dates, priorities, and statuses.
- **Status Toggling**: Dedicated endpoint to quickly toggle tasks between `PENDING` and `COMPLETED`.
- **Validation**: Strict validation for priority levels (`LOW`, `MEDIUM`, `HIGH`) and task statuses.
- **RESTful Design**: Clean URL patterns and appropriate HTTP method usage.

## 🛠️ Tech Stack
- **Framework**: Django 4.2+
- **API Toolkit**: Django REST Framework (DRF)
- **Database**: SQLite (Development)
- **Language**: Python 3.x

## 🏁 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/vbeni30/ALX-task-management-api-project.git
cd ALX-task-management-api-project
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
```bash
python manage.py makemigrations api
python manage.py migrate
```

### 5. Create a Superuser (Optional - for Admin access)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/api/`.

---

## 📖 API Documentation

### Authentication
Currently, the API uses **Session Authentication** and **Basic Authentication**. 
For Postman testing, use your "Superuser" credentials or create a user via the Django Admin. All requests must be authenticated.

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/tasks/` | List all tasks for the logged-in user. |
| `POST` | `/api/tasks/` | Create a new task. |
| `GET` | `/api/tasks/<id>/` | Retrieve details of a specific task. |
| `PUT` | `/api/tasks/<id>/` | Update a task (Full update). |
| `PATCH` | `/api/tasks/<id>/` | Partial update of a task. |
| `DELETE` | `/api/tasks/<id>/` | Remove a task. |
| `PATCH` | `/api/tasks/<id>/toggle/` | Quickly toggle status between Pending/Completed. |

### Data Model
| Field | Type | Description |
| :--- | :--- | :--- |
| `title` | `string` | Task heading (Required). |
| `description` | `text` | Detailed notes (Optional). |
| `due_date` | `date` | Expected completion date. |
| `priority` | `string` | `LOW`, `MEDIUM`, or `HIGH`. |
| `status` | `string` | `PENDING` or `COMPLETED`. |
| `completed_at`| `datetime` | Automatically set when task is completed. |

---

## 🛤️ Roadmap
This is Part 3 of the capstone project. Future phases will include:
- [ ] JWT Authentication implementation.
- [ ] Task categories/tags.
- [ ] Due date reminders and notifications.
- [ ] Advanced filtering and search.

## 📄 License
ALX SE Program Project.
