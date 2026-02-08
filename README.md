# Nurtura – Caregiving Coordination Backend

**Nurtura** is a caregiving coordination platform designed to help caregivers manage dependents, schedules, shared caregiving spaces, and daily care tasks efficiently.  
The system supports collaborative caregiving, reminders, analytics, and AI-assisted support to improve care quality and task organization.

---

## System Modules

### 1. Caregiver Modules

#### User & Authentication Module
**Purpose:** Manage caregiver accounts and secure access.

**Functions**
- Register caregiver accounts
- Secure login with authentication tokens
- View and update caregiver profile information
- Change password and manage security settings
- Deactivate or remove caregiver accounts

---

#### Dependent Profile Module
**Purpose:** Manage dependent records created by caregivers.

**Functions**
- Create dependent profiles
- View dependent information
- Update dependent details (name, age, care notes)
- Remove dependent profiles

---

#### Care Space Module
**Purpose:** Enable collaborative caregiving through shared spaces.

**Functions**
- Create, update, and delete care spaces
- Add or remove caregivers within a care space
- Assign or remove dependents to care spaces

---

#### Task Management Module
**Purpose:** Organize and manage caregiving responsibilities.

**Functions**
- Create caregiving tasks
- View assigned and created tasks
- Update task details and status
- Delete tasks

---

#### Calendar & Schedule Module
**Purpose:** Provide schedule visualization and tracking.

**Functions**
- Display tasks in calendar format
- Monitor upcoming tasks
- Identify overdue or missed tasks

---

#### Notifications & Alerts Module
**Purpose:** Provide reminders and urgent caregiving alerts.

**Functions**
- Configure notification preferences
- Send task reminders
- Notify caregivers of missed or completed tasks
- Receive urgent alerts triggered by dependents

---

#### Dashboard & Analytics Module
**Purpose:** Provide caregiving insights and quick system overview.

**Functions**
- View caregiving statistics (completed, pending, missed tasks)
- Quick access to essential caregiving actions
- Monitor caregiving workload summaries

---

#### AI Care Assistant Module
**Purpose:** Assist caregivers using AI-driven interaction.

**Functions**
- Conversational assistance
- Query schedules and task summaries
- Create simple tasks through conversational commands

---

### 2. Dependent Modules

#### User & Authentication Module
**Purpose:** Allow dependents to securely access their assigned accounts.

**Functions**
- Dependent login (caregiver-created accounts only)

---

#### Task Interaction Module
**Purpose:** Allow dependents to interact with assigned tasks.

**Functions**
- View assigned caregiving tasks
- Mark tasks as completed with one-tap action

---

#### Calendar & Schedule Module (Read-Only)
**Purpose:** Provide schedule visibility without editing permissions.

**Functions**
- View assigned tasks in calendar format
- Track deadlines and scheduled activities

---

#### Notifications & Alerts Module
**Purpose:** Provide reminders and system alerts.

**Functions**
- Receive task notifications
- Complete tasks directly from notification prompts

---

#### Dashboard Module (View-Only)
**Purpose:** Provide simplified task overview for dependents.

**Functions**
- View assigned task statistics
- Access daily task summaries
- View notifications

---

#### AI Assistant Module (Simplified)
**Purpose:** Provide simple conversational assistance.

**Functions**
- Basic conversational guidance
- Ask simple task-related questions (e.g., “What should I do now?”)

---

#### Quick Alert System Module
**Purpose:** Enable emergency communication with caregivers.

**Functions**
- One-tap emergency alert button
- Instantly notify assigned caregivers

---

## Tech Stack

- **Backend Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **ORM & Migrations:** SQLAlchemy + Alembic
- **Authentication & Security:** JWT + Passlib (bcrypt)
- **Validation & Settings:** Pydantic + Pydantic-Settings
- **Background Jobs & Scheduling:** APScheduler
- **Real-time Notifications:** WebSockets
- **AI Assistant Integration:** LLM-powered conversational assistant
- **Mobile Client:** React Native

---

## Setup / Installation
1. Clone the repo:
   ```bash
   git clone <repo-url>
   cd nurtura_backend