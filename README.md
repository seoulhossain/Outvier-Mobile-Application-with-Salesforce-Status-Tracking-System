# Outvier - International Student Application Portal

A full-stack web application that connects international students to their Salesforce CRM application records in real time.

**Stack:** Django 4.2 - Django REST Framework - React 19 - PostgreSQL - Redis - Celery - JWT Auth

---

## Team

| Member | Contributions |
|--------|---------------|
| Seoul Hossain (Team Leader) | Backend, Frontend, Salesforce CRM Integration, JWT Auth, RBAC, Database |
| Md Maruf Rahman | Backend, Frontend, Database |
| Mehadi Hasan Ayan | Backend, Frontend, Database |
| Maksudul Hoq Manik | Database, Documentation |
| Ranju Ahamed | Database, Documentation |

---

## Features

- JWT authentication with role-based access control (RBAC)
- Real-time Salesforce CRM sync via webhooks and Celery tasks
- Student portal showing application status, documents and offer details
- Admin dashboard with sync logs and full student application management
- Email and push notification system
- RESTful API with full test coverage

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 4.2, Django REST Framework |
| Frontend | React 19, Vite |
| Database | PostgreSQL |
| Cache and Queue | Redis, Celery |
| CRM Integration | Salesforce REST API |
| Auth | JWT (SimpleJWT) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Installation

Clone the repo:
git clone https://github.com/seoulhossain/Outvier-Mobile-Application-with-Salesforce-Status-Tracking-System.git
cd Outvier-Mobile-Application-with-Salesforce-Status-Tracking-System

Backend setup:
cd outvier_backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

Frontend setup:
cd outvier_frontend
npm install
npm run dev

---

## Demo Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Student | alex | alex1234 |
| Student | priya | priya5678 |
| Student | tom | tom9012 |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/token/ | Login |
| POST | /api/token/refresh/ | Refresh token |
| GET | /api/applications/ | List applications |
| GET | /api/applications/id/ | Application detail |
| GET | /api/notifications/ | Notifications |
| GET | /api/admin/sync-logs/ | Sync logs (admin only) |
| POST | /api/webhooks/salesforce/ | Salesforce webhook |

---

## Running Tests

cd outvier_backend
python manage.py test
