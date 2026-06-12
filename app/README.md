# Notes API

A small REST API for creating and listing notes. Built with FastAPI and Postgres.

## Run locally

1. Start Postgres:
   `docker compose up -d`
2. Create a virtual environment and install dependencies:
   `python -m venv .venv`
   `source .venv/Scripts/activate`
   `pip install -r requirements.txt`
3. Start the app:
   `uvicorn src.main:app --reload`
4. Open http://localhost:8000/docs to try the endpoints.

## Endpoints

- `GET /notes` — list all notes
- `POST /notes` — create a note
- `GET /notes/{id}` — get one note
- `DELETE /notes/{id}` — delete a note

## Tests

With Postgres running: `pytest`