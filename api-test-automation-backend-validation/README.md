# API Test Automation & Backend Validation Platform

A portfolio-quality REST API application and automated test framework built with Python, FastAPI, Pytest and SQLAlchemy.

The project is designed around a realistic QA workflow:

**Register → Login → Token → Project → Test Case → Execution Result → Database Validation → Report**

## What this project demonstrates

- API test automation
- Functional, regression and integration testing
- Positive and negative test design
- Request/response validation
- JWT-based authentication
- Relational database validation
- Data-driven testing with Pytest
- Reusable API client and assertion helpers
- Structured logging and failure artifacts
- HTML + JUnit reporting
- Postman collection with environment variables
- GitHub Actions CI
- Optional AI-assisted test failure analysis

## Application

The project implements a small **QA Test Management API** with:

- Users
- Authentication
- Projects
- Test cases
- Test execution results

The resources are connected with foreign-key relationships:

```text
User
  │
  ├── owns ──> Project
  │              │
  │              └── contains ──> Test Case
  │                                  │
  │                                  └── has ──> Test Result
  │
  └── authenticates through JWT
```

## API surface

### Authentication

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Users

```text
GET    /users
GET    /users/{user_id}
PUT    /users/{user_id}
DELETE /users/{user_id}
```

### Projects

```text
POST   /projects
GET    /projects
GET    /projects/{project_id}
PUT    /projects/{project_id}
DELETE /projects/{project_id}
```

### Test Cases

```text
POST   /projects/{project_id}/testcases
GET    /projects/{project_id}/testcases
GET    /testcases/{testcase_id}
PUT    /testcases/{testcase_id}
DELETE /testcases/{testcase_id}
```

### Test Results

```text
POST /testcases/{testcase_id}/results
GET  /testcases/{testcase_id}/results
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Project structure

```text
api-test-automation-backend-validation/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── dependencies.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── users.py
│       ├── projects.py
│       ├── testcases.py
│       └── results.py
│
├── tests/
│   ├── auth/
│   │   └── test_auth.py
│   ├── users/
│   │   └── test_users.py
│   ├── projects/
│   │   └── test_projects.py
│   ├── testcases/
│   │   └── test_testcases.py
│   ├── results/
│   │   └── test_results.py
│   └── integration/
│       └── test_end_to_end.py
│
├── utils/
│   ├── __init__.py
│   ├── api_client.py
│   ├── assertions.py
│   ├── db_validator.py
│   ├── logger.py
│   └── ai_failure_analyzer.py
│
├── test_data/
│   └── test_inputs.json
│
├── postman/
│   └── API_Test_Automation.postman_collection.json
│
├── reports/
│   └── .gitkeep
├── artifacts/
│   └── .gitkeep
│
├── .github/
│   └── workflows/
│       └── api-tests.yml
│
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## Windows setup

### 1. Requirements

Install:

- Python 3.11+
- Git
- Postman (optional, for manual API exploration)

Verify:

```powershell
python --version
git --version
```

### 2. Create a virtual environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy:

```powershell
Copy-Item .env.example .env
```

Default local configuration uses SQLite, so no external database is required.

### 4. Start the API

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Running the automated tests

The test suite uses an isolated in-memory SQLite database, so the tests do not modify your local `qa_test_management.db`.

Run everything:

```powershell
pytest
```

Run smoke tests:

```powershell
pytest -m smoke
```

Run functional tests:

```powershell
pytest -m functional
```

Run regression tests:

```powershell
pytest -m regression
```

Run integration tests:

```powershell
pytest -m integration
```

Run database-validation tests:

```powershell
pytest -m database
```

The default Pytest configuration writes:

```text
reports/pytest-report.html
reports/junit.xml
```

---

## Test design

The suite contains more than 30 meaningful scenarios covering:

### Authentication

- valid registration
- duplicate email
- invalid email
- missing required field
- valid login
- invalid password
- unknown account
- valid protected request
- missing token
- invalid token

### Users

- authenticated user list
- get user
- missing user
- update own profile
- invalid update data
- delete own account
- forbidden modification of another user

### Projects

- create project
- missing project name
- duplicate project
- list projects
- get project
- missing project
- update project
- delete project

### Test cases

- create test case
- invalid test case
- missing project
- list project test cases
- update test case
- delete test case

### Test results

- submit passing result
- submit failing result
- get execution history

### End-to-end flows

- register → login → project → test case → result
- login failure → protected endpoint rejection

---

## Data-driven testing

Pytest parameterization is used for groups of invalid payloads so that the same test logic can validate multiple inputs without copying test code.

The test data lives in:

```text
test_data/test_inputs.json
```

---

## Reusable API client

The tests use `utils/api_client.py` rather than repeating raw `TestClient` request code everywhere.

It provides:

```text
get()
post()
put()
delete()
login()
```

and keeps the most recent request/response exchange available for failure diagnostics.

---

## Database validation

The API tests do not stop at checking HTTP status codes.

For database-marked tests, the framework also checks the SQLite state after operations.

Example:

```text
POST /projects
        ↓
HTTP response validation
        ↓
Database query
        ↓
Verify project was actually persisted
```

This makes the project demonstrate backend validation rather than only endpoint-level checks.

---

## Postman

A ready-to-import collection is included:

```text
postman/API_Test_Automation.postman_collection.json
```

Import it into Postman.

The collection uses variables:

```text
base_url
token
user_id
project_id
testcase_id
```

Start the API first, then run the requests in order.

---

## Logging and failure artifacts

When a test fails, the framework attempts to save a useful artifact containing:

- test name
- request method
- endpoint
- safe request summary
- response status
- response body
- traceback
- timestamp

Artifacts are stored under:

```text
artifacts/failures/
```

Secrets such as passwords and bearer tokens are redacted before an artifact is written.

Runtime framework logs are stored under:

```text
artifacts/logs/
```

---

## AI-assisted test failure analysis

The AI feature is optional.

File:

```text
utils/ai_failure_analyzer.py
```

It accepts a sanitized test failure summary and produces:

```text
Failure Summary
Likely Cause
Suggested Next Step
```

Configure it through `.env`:

```text
LLM_API_URL=
LLM_API_KEY=
LLM_MODEL=
```

The analyzer expects an OpenAI-compatible chat-completions style endpoint.

If those values are not configured, the test framework continues to work and writes a note explaining that AI analysis was skipped.

Passwords and access tokens are removed before any optional AI request.

---

## CI/CD

GitHub Actions workflow:

```text
.github/workflows/api-tests.yml
```

The workflow:

1. Checks out the repository
2. Sets up Python
3. Installs dependencies
4. Runs Ruff
5. Runs Pytest
6. Generates HTML/JUnit reports
7. Uploads reports as workflow artifacts

The CI suite uses the same in-memory SQLite strategy as the local test suite, so it does not depend on an external database service.

---

## Interview talking points

Be prepared to explain:

- API testing vs UI testing
- Smoke vs functional vs regression testing
- Positive vs negative testing
- Why a reusable API client is useful
- Pytest fixtures and parameterization
- HTTP status codes
- Authentication and JWT
- Request/response validation
- Database validation
- Test data separation
- Failure artifacts and logging
- CI/CD execution
- Why the AI analyzer is optional
- How you protect secrets in logs and AI requests

---

## Resume bullet points

**API Test Automation & Backend Validation Platform — Python, FastAPI, Pytest, SQLAlchemy, SQLite, GitHub Actions**

- Built a REST-based QA Test Management API with JWT authentication, relational data models and input validation.
- Created 30+ automated API tests covering smoke, functional, regression and end-to-end workflows.
- Added reusable API clients, data-driven testing, database validation and HTML/JUnit test reporting.
- Implemented structured failure artifacts, CI execution through GitHub Actions and an optional AI-assisted failure analysis utility.

---

## Project status

The repository is intentionally designed so the core application and test suite work without requiring an external database or paid service.

The optional AI feature requires an LLM-compatible endpoint and API key.
