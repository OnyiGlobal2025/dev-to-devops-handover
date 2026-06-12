import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Config comes from the environment. The local default is only for convenience;
# in production the real connection string is injected as an env var.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:password@localhost:5432/notes",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes API")


class NoteIn(BaseModel):
    title: str
    body: str = ""


class NoteOut(NoteIn):
    id: int

    class Config:
        from_attributes = True


@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")


@app.get("/notes", response_model=list[NoteOut])
def list_notes():
    db = SessionLocal()
    notes = db.query(Note).order_by(Note.id).all()
    db.close()
    return notes


@app.post("/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteIn):
    db = SessionLocal()
    obj = Note(title=note.title, body=note.body)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    db.close()
    return obj


@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    db = SessionLocal()
    obj = db.get(Note, note_id)
    db.close()
    if obj is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return obj


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    db = SessionLocal()
    obj = db.get(Note, note_id)
    if obj is None:
        db.close()
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(obj)
    db.commit()
    db.close()
    return None