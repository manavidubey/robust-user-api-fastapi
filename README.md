# Robust User Registration API

A REST API endpoint built with Flask that provides user registration functionality with comprehensive error handling, rate limiting, and retry logic.

## Features

- Accepts JSON payload with user data
- Validates input (email format, required fields)
- Implements rate limiting (max 10 requests/minute per user)
- Handles errors gracefully with proper HTTP codes
- Includes retry logic for external API calls
- Over 90% test coverage

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main_runner.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### POST /users

Registers a new user with the provided data.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

**Responses:**
- `201`: User registered successfully
- `400`: Validation failed
- `429`: Rate limit exceeded
- `500`: Internal server error

## Architecture

- **Framework**: Flask
- **Rate Limiting**: Flask-Limiter
- **Retry Logic**: retrying library
- **Validation**: Built-in regex and field validation