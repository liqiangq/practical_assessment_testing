# Tokenization Service (Python FastAPI)

A simple tokenization and detokenization REST service built with Python FastAPI.

This project was developed as part of a technical coding exercise.

## Overview

This service converts sensitive account numbers into random 32-character tokens and allows converting them back when required.
It uses an in-memory SQLite database and does not rely on any external systems.

Current behavior:

- Tokenization is idempotent: the same account number always returns the same token.
- Detokenization validates token format before lookup.
- Invalid requests return structured JSON error responses.
- The implementation includes tests for round-trip behavior and validation edge cases.

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite In-Memory Database
- pytest
- Uvicorn

## Prerequisites

Before running this project, please ensure you have:

- Python 3.11 or later
- Git (optional, for cloning)

Check Python version:

```bash
python --version
```

If needed, you can also check:

```bash
python3 --version
```

## Create and Activate Virtual Environment

Mac/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn app.main:app --reload --port 3000
```

The service starts on `http://localhost:3000`.

## Demo

Start the application:

```bash
.venv/bin/python -m uvicorn app.main:app --reload --port 3000
```

Open the Swagger API docs in your browser:

```text
http://localhost:3000/docs
```

From the Swagger page, expand `POST /tokenize` or `POST /detokenize`, click `Try it out`, enter a JSON array, and execute the request.

## Run Tests

```bash
.venv/bin/python -m pytest -vv
```

## API

### Tokenize

```bash
curl -X POST http://localhost:3000/tokenize \
-H "Content-Type: application/json" \
-d '["<Acct1>","<Acct2>"]'
```

Example response:

```json
[
  "4sR4m6R1M4m8N3qk9Q0x2Y2nP7gH1aBc",
  "f3D7kL9mN0pQ2rS4tU6vW8xY1zA3bC5d"
]
```

### Detokenize

```bash
curl -X POST http://localhost:3000/detokenize \
-H "Content-Type: application/json" \
-d '["<TOKEN1>","<TOKEN2>"]'
```

Example error response:

```json
{
  "status": 400,
  "error": "Bad Request",
  "message": "Invalid token format. Expected 32 characters in [0-9A-Za-z].",
  "path": "/detokenize"
}
```

## Notes

This implementation is intentionally lightweight for a coding exercise.
It focuses on correctness, clarity, testability, and fast local setup rather than production hardening.
