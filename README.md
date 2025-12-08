# Reel by Fontenot's Robots – CS 3200 Fall 2025 Project

## Project Overview

_Reel by Fontenot’s Robots_ is a creator-focused content platform that supports multiple roles:
- **Admins** – review creator applications, monitor system health, and moderate flagged activity.
- **Creators** – manage portfolios and projects representing their work.
- **Community / Social Users** – create posts and send messages.
- **Analytics Users** – view insights, trending tags, and creator discovery features.

---

## REST API Implementation

Our team built the full REST API structure based on our REST Matrix and user stories.

### Four Blueprint Modules

Each blueprint contains **5 or more routes**, meeting the project requirement.

---

### 1. Admin Blueprint (`admin_routes.py`)

Handles application review and system oversight.

Routes implemented:

- `GET /admin/applications`  
- `GET /admin/applications/<id>`  
- `PUT /admin/applications/<id>`  
- `DELETE /admin/applications/<id>`  
- `GET /admin/flagged-activities`  
- `POST /admin/flagged-activities`  
- `PUT /admin/flagged-activities/<id>`  
- `DELETE /admin/flagged-activities/<id>`  
- `GET /admin/alerts`  
- `POST /admin/alerts`  
- `PUT /admin/alerts/<id>`  
- `DELETE /admin/alerts/<id>`  
- `GET /admin/system-metrics`  

---

### 2. Creator Blueprint (`creator_routes.py`)

Manages creator workflows including portfolios, projects, users, and nested resources.

Core routes:

- `GET /creator/portfolios`  
- `POST /creator/portfolios`  
- `GET /creator/portfolios/<id>`  
- `PUT /creator/portfolios/<id>`  
- `DELETE /creator/portfolios/<id>`  
- `GET /creator/projects`  
- `POST /creator/projects`  
- `GET /creator/projects/<id>`  
- `PUT /creator/projects/<id>`  
- `DELETE /creator/projects/<id>`  

User and creator management:

- `GET /creator/users`  
- `GET /creator/users/<id>`  
- `PUT /creator/users/<id>`  
- `DELETE /creator/users/<id>`  
- `GET /creator/creators`  

Nested project resources:

**Project Credits**  
- `GET /creator/projects/<projectID>/credits`  
- `POST /creator/projects/<projectID>/credits`  
- `PUT /creator/projects/<projectID>/credits/<creditID>`  
- `DELETE /creator/projects/<projectID>/credits/<creditID>`  

**Project Media**  
- `GET /creator/projects/<projectID>/media`  
- `POST /creator/projects/<projectID>/media`  
- `PUT /creator/projects/<projectID>/media` (bulk update)  
- `DELETE /creator/projects/<projectID>/media/<mediaID>`  

---

### 3. Social Blueprint (`social_routes.py`)

Implements the platform's posting, interaction tracking, and messaging system.

Posts:

- `GET /social/posts`  
- `POST /social/posts`  
- `PUT /social/posts/<id>`  
- `DELETE /social/posts/<id>`  

Post interactions:

- `GET /social/post-interactions`  
- `POST /social/post-interactions`  
- `DELETE /social/post-interactions/<id>`  

Messages:

- `GET /social/messages`  
- `POST /social/messages`  
- `PUT /social/messages/<id>`  
- `DELETE /social/messages/<id>`  

---

### 4. Analytics Blueprint (`analytics_routes.py`)

Supports insights, KPI tracking, and trending metadata.

Trend Tags:

- `GET /analytics/trend-tags`  
- `POST /analytics/trend-tags`  
- `PUT /analytics/trend-tags/<id>`  
- `DELETE /analytics/trend-tags/<id>`  

KPIs:

- `GET /analytics/kpis`  
- `POST /analytics/kpis`  
- `PUT /analytics/kpis/<id>`  
- `DELETE /analytics/kpis/<id>`  

Insight Reports:

- `GET /analytics/insight-reports`  
- `POST /analytics/insight-reports`  
- `PUT /analytics/insight-reports/<id>`  
- `DELETE /analytics/insight-reports/<id>`  

---

## HTTP Methods Used Across the API

All required HTTP methods are implemented across multiple blueprints:

- **GET** – fetch resources  
- **POST** – create new resources  
- **PUT** – update existing resources  
- **DELETE** – implemented in admin, creator, social, and analytics modules  

---

## Running the Project

Start the system using Docker:

- docker compose down -v
- docker compose up --build




pages/11_Prediction.py`. Here, I create two numeric input fields. When the button is pressed, it makes a request to the REST API URL `/c/prediction/.../...` function and passes the values from the two inputs as URL parameters. It gets back the results from the route and displays them. Nothing fancy here.
hello
