<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->

[![Python][python-shield]][python-url]
[![FastAPI][fastapi-shield]][fastapi-url]
[![PostgreSQL][postgresql-shield]][postgresql-url]
[![Docker][docker-shield]][docker-url]

<!-- PROJECT LOGO -->

<br />
<div align="center">
  <h1 align="center">Nurtura</h1>

  <p align="center">
    A caregiving coordination backend for managing dependents, tasks, schedules, shared care spaces, and AI-assisted support.
    <br />
    <br />
    <a href="#about-the-project">About</a>
    &middot;
    <a href="#getting-started">Getting Started</a>
    &middot;
    <a href="#usage">Usage</a>
  </p>
</div>

---

## Table of Contents

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
        <li><a href="#system-workflow">System Workflow</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#environment-variables">Environment Variables</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#system-architecture">System Architecture</a></li>
    <li><a href="#database-structure">Database Structure</a></li>
    <li><a href="#authentication--security">Authentication & Security</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

---

## About The Project

**Nurtura** is a caregiving coordination platform designed to help caregivers manage dependents, schedules, shared caregiving spaces, and daily care responsibilities.

The system provides a centralized backend for organizing caregiving tasks, monitoring schedules, managing collaborative care spaces, and communicating important notifications between caregivers and dependents.

Nurtura also includes analytics and an AI-powered care assistant to help caregivers understand their workload, query task and schedule information, and perform simple caregiving actions through conversational interaction.

The backend is built around a modular architecture with secure RESTful APIs, PostgreSQL data storage, JWT-based authentication, scheduled background tasks, and real-time communication capabilities.

### Key Features

- Caregiver account registration and authentication
- Dependent profile management
- Shared caregiving spaces
- Caregiver and dependent task management
- Calendar and schedule tracking
- Task reminders and notifications
- Caregiving workload analytics
- AI-assisted caregiving support
- Conversational task and schedule queries
- Real-time communication through WebSockets
- Quick emergency alerts for dependents
- Role-based access between caregivers and dependents
- Secure password hashing and JWT authentication
- RESTful API architecture

### System Workflow

```text
                         Nurtura Backend
                               │
                ┌──────────────┴──────────────┐
                │                             │
           Caregivers                     Dependents
                │                             │
        ┌───────┼────────┐            ┌───────┼────────┐
        │       │        │            │       │        │
     Tasks   Schedules  Care       Tasks   Calendar  Alerts
        │               Spaces       │
        │                 │          │
        └──────────┬──────┴──────────┘
                   │
                   ▼
              FastAPI API
                   │
        ┌──────────┼───────────┐
        │          │           │
        ▼          ▼           ▼
   PostgreSQL  WebSockets   Scheduler
        │          │           │
        └──────────┼───────────┘
                   │
                   ▼
             AI Care Assistant
```

---

## Built With

The project uses the following technologies and frameworks:

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations

### Authentication & Security

- JWT
- Passlib
- bcrypt
- Password hashing
- Token-based authentication

### Real-Time & Background Processing

- WebSockets
- APScheduler
- Background task processing

### AI Integration

- Gemini AI API
- LLM-powered conversational assistant

### Deployment

- Docker
- Render

---

## Getting Started

Follow the steps below to set up the Nurtura backend locally.

### Prerequisites

Make sure the following are installed before running the application.

- Python 3.11+
- pip
- PostgreSQL
- Git
- Docker (optional)
- A configured AI API key if AI features are enabled

You can verify the installed versions using:

```sh
python --version
pip --version
psql --version
git --version
```

---

### Installation

#### 1. Clone the Repository

```sh
git clone https://github.com/ralphgacusan/nurtura-backend.git
cd nurtura-backend
```

#### 2. Create a Virtual Environment

```sh
python -m venv venv
```

Activate the environment:

**Windows**

```sh
venv\Scripts\activate
```

**Linux / macOS**

```sh
source venv/bin/activate
```

#### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/nurtura

SECRET_KEY=your-secret-key
ALGORITHM=HS256

GEMINI_API_KEY=your-api-key
```

Do not commit `.env` files or API credentials to the repository.

#### 5. Run Database Migrations

Apply the existing Alembic migrations:

```sh
alembic upgrade head
```

#### 6. Start the FastAPI Server

```sh
uvicorn app.main:app --reload
```

The API will be available locally through the configured host and port.

FastAPI also provides interactive API documentation through Swagger UI.

---

## Environment Variables

The application uses environment variables to keep credentials, database configuration, and deployment-specific settings outside the source code.

| Variable         | Description                            |
| ---------------- | -------------------------------------- |
| `DATABASE_URL`   | PostgreSQL database connection string  |
| `SECRET_KEY`     | Secret key used for JWT authentication |
| `ALGORITHM`      | JWT signing algorithm                  |
| `GEMINI_API_KEY` | API key used by the AI care assistant  |

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/nurtura
SECRET_KEY=your-secret-key
ALGORITHM=HS256
GEMINI_API_KEY=your-api-key
```

Environment variables should be configured separately for development and production environments.

---

## Usage

### 1. Create a Caregiver Account

Caregivers can register an account and authenticate using JWT-based access tokens.

Once authenticated, caregivers can access protected caregiving resources.

### 2. Manage Dependents

Caregivers can create and manage dependent profiles.

Dependent records may contain information such as:

- Name
- Age
- Care notes
- Assigned caregiver relationships

### 3. Create a Care Space

Caregivers can create shared care spaces for collaborative caregiving.

A care space can contain:

- Multiple caregivers
- Assigned dependents
- Shared caregiving tasks

This allows multiple caregivers to coordinate responsibilities within the same environment.

### 4. Manage Caregiving Tasks

Caregivers can create and manage tasks assigned to themselves or other caregivers.

Tasks can be:

- Created
- Viewed
- Updated
- Completed
- Deleted

Task status can be used to identify completed, pending, overdue, and missed responsibilities.

### 5. Monitor Schedules

The calendar and scheduling functionality allows caregivers to monitor upcoming caregiving responsibilities.

Users can identify:

- Upcoming tasks
- Scheduled activities
- Overdue tasks
- Missed tasks

### 6. Receive Notifications

The system provides reminders and alerts related to caregiving activities.

Notifications can be triggered by:

- Upcoming tasks
- Missed tasks
- Completed tasks
- Urgent dependent alerts

### 7. Use the AI Care Assistant

Caregivers can interact with the AI assistant using conversational requests.

Example queries include:

```text
What tasks do I have today?
What should I do next?
Show me my upcoming tasks.
Create a task for tomorrow.
```

The assistant can provide task and schedule information and perform supported simple task operations.

### 8. Dependent Access

Dependents can access caregiver-created accounts with limited permissions.

They can:

- View assigned tasks
- Mark tasks as completed
- View their schedules
- Receive notifications
- View task statistics
- Ask simple task-related questions

### 9. Quick Emergency Alert

Dependents can use the quick alert function to notify assigned caregivers during urgent situations.

The system sends the alert to the appropriate caregiver through the configured notification mechanism.

---

## System Architecture

Nurtura follows a **modular RESTful backend architecture** built with FastAPI.

### API Layer

FastAPI provides the main REST API used by the client application.

The API handles:

- Authentication
- Caregiver management
- Dependent management
- Care spaces
- Tasks
- Schedules
- Notifications
- Analytics
- AI assistant requests
- Emergency alerts

### Application Layer

The application layer contains the business logic responsible for coordinating caregiving operations.

It handles:

- Permission validation
- Task management
- Caregiver-dependent relationships
- Care space membership
- Notification logic
- Scheduling
- Analytics
- AI assistant operations

### Data Layer

SQLAlchemy provides the ORM layer used to communicate with PostgreSQL.

Alembic manages database schema migrations.

```text
Client Application
       │
       ▼
   FastAPI API
       │
       ├──────────────► Authentication
       │
       ├──────────────► Caregiving Modules
       │
       ├──────────────► Notifications
       │
       ├──────────────► Analytics
       │
       └──────────────► AI Assistant
       │
       ▼
    SQLAlchemy
       │
       ▼
   PostgreSQL
```

### Real-Time Communication

WebSockets are used to support real-time communication between the backend and connected clients.

This allows the system to provide timely updates without relying entirely on repeated client polling.

### Background Scheduling

APScheduler is used to handle scheduled operations such as task reminders and time-based caregiving notifications.

---

## Database Structure

Nurtura uses PostgreSQL as its primary relational database.

The database is accessed through SQLAlchemy and managed through Alembic migrations.

### Core Relationships

```text
Caregiver
   │
   ├──────────────► Care Space
   │                     │
   │                     ├──────────► Caregiver
   │                     │
   │                     └──────────► Dependent
   │
   ├──────────────► Task
   │                     │
   │                     └──────────► Schedule
   │
   └──────────────► Notification

Dependent
   │
   ├──────────────► Task
   │
   ├──────────────► Schedule
   │
   └──────────────► Emergency Alert
```

The relational structure allows caregiving information to remain connected across caregivers, dependents, care spaces, tasks, schedules, and notifications.

---

## Authentication & Security

Nurtura uses token-based authentication to protect API resources.

### Authentication

The system uses:

- JWT access tokens
- Secure password hashing
- Passlib
- bcrypt

Authenticated requests require a valid access token when accessing protected endpoints.

### Authorization

Different permissions are applied depending on whether the authenticated user is a caregiver or dependent.

Caregivers can manage caregiving resources, while dependents have restricted access to assigned tasks, schedules, notifications, and other permitted functionality.

### Password Security

Passwords are never stored as plain text.

Passwords are hashed using bcrypt before being stored in the database.

---

## API Documentation

FastAPI automatically provides interactive API documentation.

When running the application locally, the documentation can be accessed through:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI specification is also available through:

```text
http://127.0.0.1:8000/openapi.json
```

The documentation can be used to inspect available endpoints, request parameters, authentication requirements, and response schemas.

---

## Roadmap

- [x] Caregiver authentication
- [x] Dependent account management
- [x] Dependent profile management
- [x] Shared care spaces
- [x] Caregiving task management
- [x] Calendar and scheduling
- [x] Notifications and alerts
- [x] Dashboard and analytics
- [x] AI care assistant
- [x] JWT authentication
- [x] PostgreSQL integration
- [x] SQLAlchemy ORM
- [x] Alembic database migrations
- [x] WebSocket communication
- [x] Scheduled background tasks
- [x] Docker support
- [x] Cloud deployment
- [ ] Expand AI-assisted caregiving workflows
- [ ] Improve notification delivery
- [ ] Expand analytics and reporting
- [ ] Support additional caregiving integrations

---

## Contributing

Contributions are welcome and appreciated.

1. Fork the Project
2. Create your Feature Branch

```sh
git checkout -b feature/AmazingFeature
```

3. Commit your Changes

```sh
git commit -m "Add AmazingFeature"
```

4. Push to the Branch

```sh
git push origin feature/AmazingFeature
```

5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Contact

**Project:** Nurtura – Caregiving Coordination Backend

**Project Repository:**

```text
https://github.com/ralphgacusan/nurtura-backend
```

**Project Demo:**

```text
https://nurtura-backend-zgz8.onrender.com
```

---

## Acknowledgments

- FastAPI
- Python
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Passlib
- bcrypt
- Docker
- Render
- Gemini AI

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/
[fastapi-shield]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[postgresql-shield]: https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white
[postgresql-url]: https://www.postgresql.org/
[docker-shield]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[docker-url]: https://www.docker.com/
