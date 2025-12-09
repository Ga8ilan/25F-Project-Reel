# Reel - CS 3200 Fall 2025 Project

**Team: Fontenot's Robots**

## Team Members

- **William Huang** - Admin Persona (Platform Administrator)
- **Sanshubh Rath** - Analytics Persona (Data Analyst - Chris Parker)
- **Edgar Castaneda** - Creator Persona (Mike Walston)
- **Lynette Dong** - Community Persona (Veronica Fuller)


## Project Overview

**Reel** is an invite-only, portfolio-first professional network built for creatives and the brands that hire them. Where LinkedIn overwhelms with noise and generic resumes, Reel elevates proven creative work by showcasing reels, credits, and verified collaborators.

The platform curates a high-quality ecosystem of filmmakers, designers, animators, photographers, editors, musicians, and creative directors, alongside vetted companies and agencies seeking talent. By collecting structured portfolio data, analyzing collaboration networks, and tracking availability and project metadata, Reel helps both sides make faster, better-informed decisions.

### Key Features

- **Portfolio Management**: Creators can upload and organize their work with verified credits
- **Collaboration Networks**: Verified collaborator relationships and credit tracking
- **Social Features**: Posts, messaging, and community interactions
- **Analytics Dashboard**: Rising creators, trend analysis, and KPI tracking
- **Admin Tools**: Application review, system monitoring, and content moderation


## Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Flask REST API (Python)
- **Database**: MySQL 9
- **Containerization**: Docker & Docker Compose

## Prerequisites

- **Docker**
- **Docker Compose**

To verify installation:
```bash
docker --version
docker compose version
```


## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd 25F-Project-Reel
```

### 2. Create Environment File

Create a `.env` file in the `api/` directory with the following content:

```bash
cd api
```

Create a file named `.env` with:

```
SECRET_KEY=dev-secret-key-123
DB_USER=root
MYSQL_ROOT_PASSWORD=rootpassword
DB_HOST=db
DB_PORT=3306
DB_NAME=reel_db
```

These are Just placeholder values so dont worry. 

### 3. Start the Application

From the project root directory:

```bash
docker compose down -v
docker compose up --build
```

## Running the Application

Once containers are running, access the application at:

- **Streamlit Frontend**: http://localhost:8501
- **Flask API**: http://localhost:4000
- **MySQL Database**: localhost:3200

### User Roles

The application supports four personas. From the login page, you can act as:

1. **William** - Platform Administrator
2. **Chris Parker** - Data Analyst
3. **Mike Walston** - Creator
4. **Veronica Fuller** - Community User

---

## API Documentation

### REST API Structure

The backend implements a RESTful API with four main blueprint modules:

#### 1. Admin Routes (`/admin`)
- Application review and approval
- System alerts and metrics
- Flagged activity moderation

#### 2. Creator Routes (`/creator`)
- Portfolio management
- Project and credit management
- User profile management
- Nested resources (project credits, media)

#### 3. Social Routes (`/social`)
- Post creation and management
- Post interactions (likes, comments)
- Messaging system

#### 4. Analytics Routes (`/analytics`)
- Trend tag management
- KPI configuration and tracking
- Insight report generation

### HTTP Methods

All blueprints implement standard REST operations:
- **GET**: Retrieve resources
- **POST**: Create new resources
- **PUT**: Update existing resources
- **DELETE**: Remove resources


## Database Management

### Initialization

SQL files in `database-files/` are automatically executed when the MySQL container is first created. Files run in alphabetical order:
1. `01_reel_db.sql` - Creates database schema
2. `02_mock_data.sql` - Inserts sample data

### Reinitializing Database

If you modify SQL files and need to recreate the database:

```bash
docker compose down db -v
docker compose up db -d
```

The `-v` flag removes the MySQL volume, forcing re-initialization with updated SQL files.

### Containers Won't Start

- Ensure Docker is running
- Check that port 8501, 4000, and 3200 are not in use
- Verify `.env` file exists in `api/` directory with correct format

## Development Notes

- Frontend code changes are hot-reloaded via volume mounts
- Backend code changes require container restart for some files
- Database changes require volume removal and container recreation
- SQL files only execute on initial container creation, not on restart
