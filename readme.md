# Quiz API

A RESTful API for managing quizzes with multiple-choice questions. Administrators can create and manage quizzes, while users can take quizzes publicly without authentication.

## Features

- 🔐 Token-based authentication for admins
- ✏️ Complete CRUD operations for quizzes and questions
- 📝 Multiple-choice questions with 2-6 options
- 🎯 Public quiz taking (no authentication required)
- ⚡ Instant scoring and feedback
- ✅ Comprehensive input validation

## Technology Stack

- **Framework:** Django 5.x
- **API Framework:** Django REST Framework
- **Database:** SQLite
- **Authentication:** Token-based

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to project directory**
```bash
cd quiz_api
```

2. **Create and activate virtual environment**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install django djangorestframework
```

4. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Start the development server**
```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

## API Endpoints

### Base URL
```
http://127.0.0.1:8000/api/
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new admin | ❌ |
| POST | `/api/auth/login/` | Login admin | ❌ |
| POST | `/api/auth/logout/` | Logout admin | ✅ |

### Quiz Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/quizzes/` | Create quiz | ✅ |
| GET | `/api/quizzes/` | List all quizzes | ❌ |
| GET | `/api/quizzes/{id}/` | Get quiz details | ❌ |
| PUT/PATCH | `/api/quizzes/{id}/` | Update quiz | ✅ |
| DELETE | `/api/quizzes/{id}/` | Delete quiz | ✅ |

### Question Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/questions/` | Add question | ✅ |
| GET | `/api/questions/` | List all questions | ✅ |
| GET | `/api/questions/?quiz_id={id}` | Filter by quiz | ✅ |
| GET | `/api/questions/{id}/` | Get question details | ✅ |
| PUT/PATCH | `/api/questions/{id}/` | Update question | ✅ |
| DELETE | `/api/questions/{id}/` | Delete question | ✅ |

### Quiz Taking Endpoints (Public)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/quizzes/{id}/take/` | Get quiz questions | ❌ |
| POST | `/api/quizzes/{id}/submit/` | Submit answers | ❌ |

## Testing Guide

### 1. Register an Admin

**Request:**
```http
POST http://127.0.0.1:8000/api/auth/register/
Content-Type: application/json
```

**Body:**
```json
{
    "username": "admin",
    "email": "admin@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "message": "Admin user created successfully",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

💡 **Save the token for authenticated requests!**

### 2. Login

**Request:**
```http
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json
```

**Body:**
```json
{
    "username": "admin",
    "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_id": 1,
    "username": "admin",
    "email": "admin@example.com"
}
```

### 3. Create a Quiz

**Request:**
```http
POST http://127.0.0.1:8000/api/quizzes/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body:**
```json
{
    "title": "Python Programming Quiz"
}
```

**Response (201 Created):**
```json
{
    "message": "Quiz created successfully",
    "data": {
        "id": 1,
        "title": "Python Programming Quiz",
        "created_at": "2025-10-05T10:30:00Z"
    }
}
```

### 4. Add Questions to Quiz

**Request:**
```http
POST http://127.0.0.1:8000/api/questions/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body:**
```json
{
    "quiz": 1,
    "text": "What is the capital of France?",
    "options": [
        {
            "text": "London",
            "is_correct": false
        },
        {
            "text": "Paris",
            "is_correct": true
        },
        {
            "text": "Berlin",
            "is_correct": false
        },
        {
            "text": "Madrid",
            "is_correct": false
        }
    ]
}
```

**Response (201 Created):**
```json
{
    "message": "Question created successfully",
    "data": {
        "id": 1,
        "quiz": 1,
        "quiz_title": "Python Programming Quiz",
        "text": "What is the capital of France?",
        "options": [
            {
                "id": 1,
                "text": "London",
                "is_correct": false
            },
            {
                "id": 2,
                "text": "Paris",
                "is_correct": true
            },
            {
                "id": 3,
                "text": "Berlin",
                "is_correct": false
            },
            {
                "id": 4,
                "text": "Madrid",
                "is_correct": false
            }
        ],
        "created_at": "2025-10-05T11:00:00Z"
    }
}
```

### 5. List All Quizzes (Public)

**Request:**
```http
GET http://127.0.0.1:8000/api/quizzes/
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "message": "Quizzes retrieved successfully",
    "count": 2,
    "data": [
        {
            "id": 1,
            "title": "Python Programming Quiz",
            "created_at": "2025-10-05T10:30:00Z"
        },
        {
            "id": 2,
            "title": "JavaScript Fundamentals",
            "created_at": "2025-10-05T11:00:00Z"
        }
    ]
}
```

### 6. Take a Quiz (Public - No Authentication)

**Request:**
```http
GET http://127.0.0.1:8000/api/quizzes/1/take/
Content-Type: application/json
```

**Response (200 OK):**
```json
{
    "message": "Quiz questions retrieved successfully",
    "quiz_title": "Python Programming Quiz",
    "total_questions": 2,
    "data": [
        {
            "id": 1,
            "text": "What is the capital of France?",
            "options": [
                {
                    "id": 1,
                    "text": "London"
                },
                {
                    "id": 2,
                    "text": "Paris"
                },
                {
                    "id": 3,
                    "text": "Berlin"
                },
                {
                    "id": 4,
                    "text": "Madrid"
                }
            ]
        },
        {
            "id": 2,
            "text": "What is 2 + 2?",
            "options": [
                {
                    "id": 5,
                    "text": "3"
                },
                {
                    "id": 6,
                    "text": "4"
                },
                {
                    "id": 7,
                    "text": "5"
                }
            ]
        }
    ]
}
```

📌 **Note:** The `is_correct` field is NOT included in the response!

### 7. Submit Quiz Answers (Public - No Authentication)

**Request:**
```http
POST http://127.0.0.1:8000/api/quizzes/1/submit/
Content-Type: application/json
```

**Body:**
```json
{
    "answers": [
        {
            "question_id": 1,
            "option_id": 2
        },
        {
            "question_id": 2,
            "option_id": 6
        }
    ]
}
```

**Response (200 OK):**
```json
{
    "message": "Quiz submitted successfully",
    "score": 2,
    "total": 2,
    "percentage": 100.0
}
```

### 8. Update Quiz (Requires Authentication)

**Request:**
```http
PATCH http://127.0.0.1:8000/api/quizzes/1/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Body:**
```json
{
    "title": "Advanced Python Quiz"
}
```

**Response (200 OK):**
```json
{
    "message": "Quiz updated successfully",
    "data": {
        "id": 1,
        "title": "Advanced Python Quiz",
        "created_at": "2025-10-05T10:30:00Z"
    }
}
```

### 9. Delete Quiz (Requires Authentication)

**Request:**
```http
DELETE http://127.0.0.1:8000/api/quizzes/1/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response (200 OK):**
```json
{
    "message": "Quiz \"Advanced Python Quiz\" deleted successfully"
}
```

### 10. Logout (Requires Authentication)

**Request:**
```http
POST http://127.0.0.1:8000/api/auth/logout/
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response (200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

## Authentication

The API uses token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your_token_here
```

**Example:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Error Responses

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input/validation error |
| 401 | Unauthorized | Authentication required or invalid token |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Common Errors

**Authentication Error:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Validation Error:**
```json
{
    "error": "Validation failed",
    "details": {
        "title": ["Quiz title is required."]
    }
}
```

**Not Found Error:**
```json
{
    "error": "Quiz not found"
}
```

## Validation Rules

### Quiz
- Title: 3-200 characters, required
- Must contain at least one alphanumeric character
- Cannot be duplicate (case-insensitive)

### Question
- Text: Minimum 5 characters, required
- Options: 2-6 options required
- Exactly one option must be marked as correct
- Options cannot be duplicate (case-insensitive)

### Option
- Text: 1-200 characters, required
- Must contain at least one alphanumeric character
- `is_correct`: Boolean, required

## Troubleshooting

### "Authentication credentials were not provided"
Make sure you include the Authorization header:
```
Authorization: Token your_token_here
```

### "Invalid token"
Token may have expired or been deleted. Login again to get a new token.

### "Quiz not found"
Check that the quiz ID exists. Use `GET /api/quizzes/` to see available quizzes.

### Server not running
Start the server:
```bash
python manage.py runserver
```

### Database errors
Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Quick Start Summary

1. **Setup:** Install dependencies, run migrations, start server
2. **Register:** Create admin account via `/api/auth/register/`
3. **Login:** Get token via `/api/auth/login/`
4. **Create Quiz:** POST to `/api/quizzes/` with token
5. **Add Questions:** POST to `/api/questions/` with token
6. **Take Quiz:** GET `/api/quizzes/{id}/take/` (no token needed)
7. **Submit:** POST `/api/quizzes/{id}/submit/` with answers
8. **Get Score:** Receive instant feedback

## License

This project is open source and available for educational purposes.