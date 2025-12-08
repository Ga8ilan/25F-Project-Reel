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




1. We need to turn off the standard panel of links on the left side of the Streamlit app. This is done through the `app/src/.streamlit/config.toml` file. So check that out. We are turning it off so we can control directly what links are shown.
1. Then I created a new python module in `app/src/modules/nav.py`. When you look at the file, you will se that there are functions for basically each page of the application. The `st.sidebar.page_link(...)` adds a single link to the sidebar. We have a separate function for each page so that we can organize the links/pages by role.
1. Next, check out the `app/src/Home.py` file. Notice that there are 3 buttons added to the page and when one is clicked, it redirects via `st.switch_page(...)` to that Roles Home page in `app/src/pages`. But before the redirect, I set a few different variables in the Streamlit `session_state` object to track role, first name of the user, and that the user is now authenticated.
1. Notice near the top of `app/src/Home.py` and all other pages, there is a call to `SideBarLinks(...)` from the `app/src/nav.py` module. This is the function that will use the role set in `session_state` to determine what links to show the user in the sidebar.
1. The pages are organized by Role. Pages that start with a `0` are related to the _Political Strategist_ role. Pages that start with a `1` are related to the _USAID worker_ role. And, pages that start with a `2` are related to The _System Administrator_ role.


## (Completely Optional) Incorporating ML Models into your Project

_Note_: This project only contains the infrastructure for a hypothetical ML model.

1. Collect and preprocess necessary datasets for your ML models.
1. Build, train, and test your ML model in a Jupyter Notebook.
   - You can store your datasets in the `datasets` folder. You can also store your Jupyter Notebook in the `ml-src` folder.
1. Once your team is happy with the model's performance, convert your Jupyter Notebook code for the ML model to a pure Python script.
   - You can include the `training` and `testing` functionality as well as the `prediction` functionality.
   - Develop and test this pure Python script first in the `ml-src` folder.
   - You may or may not need to include data cleaning, though.
1. Review the `api/backend/ml_models` module. In this folder,
   - We've put a sample (read _fake_) ML model in the `model01.py` file. The `predict` function will be called by the Flask REST API to perform '_real-time_' prediction based on model parameter values that are stored in the database. **Important**: you would never want to hard code the model parameter weights directly in the prediction function.
1. The prediction route for the REST API is in `api/backend/customers/customer_routes.py`. Basically, it accepts two URL parameters and passes them to the `prediction` function in the `ml_models` module. The `prediction` route/function packages up the value(s) it receives from the model's `predict` function and send its back to Streamlit as JSON.
1. Back in streamlit, check out `app/src/pages/11_Prediction.py`. Here, I create two numeric input fields. When the button is pressed, it makes a request to the REST API URL `/c/prediction/.../...` function and passes the values from the two inputs as URL parameters. It gets back the results from the route and displays them. Nothing fancy here.
hello
