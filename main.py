from pathlib import Path

from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./openings.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase): pass


class Opening(Base):
    __tablename__ = "opening"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_path = Column(String)
    difficulty = Column(Integer)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

app = FastAPI()

root_folder = Path("openings")
db = SessionLocal()


@app.get("/")
def main():
    return FileResponse("index.html")


@app.get("/api/openings")
def get_openings():
    return db.query(Opening).all()


@app.get("/api/opening/{id}")
def get_opening(id):
    opening = db.query(Opening).filter(Opening.id == id).first()
    if opening is None:
        return JSONResponse(status_code=404, content={"message": "не найден"})
    return opening


@app.get("/api/download_opening/{id}")
def download_file(id):
    opening = db.query(Opening).filter(Opening.id == id).first()
    return FileResponse(path=str(opening.file_path))


@app.post("/api/openings")
def create_opening(data=Body()):
    opening = Opening(name=data["name"], file_path=data["file_path"], difficulty=data["difficulty"])
    db.add(opening)
    db.commit()
    db.refresh(opening)
    return opening


@app.put("/api/openings")
def edit_opening(data=Body()):
    opening = db.query(Opening).filter(Opening.id == data["id"]).first()
    if opening is None:
        return JSONResponse(status_code=404, content={"message": "не найден"})
    opening.name = data["name"]
    opening.file_path = data["file_path"]
    opening.difficulty = data["difficulty"]
    db.commit()
    db.refresh(opening)
    return opening


@app.delete("/api/opening/{id}")
def delete_opening(id):
    opening = db.query(Opening).filter(Opening.id == id).first()
    if opening is None:
        return JSONResponse(status_code=404, content={"message": "не найден"})
    db.delete(opening)
    db.commit()
    return opening
