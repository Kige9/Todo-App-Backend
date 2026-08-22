from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from uuid import uuid4
from contextlib import asynccontextmanager




DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/comments_db"
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)


class BaseCommentORM(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class CommentORM(BaseCommentORM):
    __tablename__ = "comments"

    author: Mapped[str]
    text: Mapped[str]


class CreateCommentSchema(BaseModel):
    author: str
    text: str

class UpdateCommentSchema(BaseModel):
    author: str | None = None
    text: str | None = None

class CommentSchema(BaseModel):
    id: str
    author: str
    text: str

    class Config:
        from_attributes = True

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(_: FastAPI):
    BaseCommentORM.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/comments", status_code=201, response_model=CommentSchema)
def create_comment(payload: CreateCommentSchema, db: Session = Depends(get_db)):
    new_comment = CommentORM(author=payload.author, text=payload.text)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/comments", response_model=list[CommentSchema])
def get_comments(db: Session = Depends(get_db)):
    comments_from_db = db.scalars(select(CommentORM)).all()
    return comments_from_db


@app.delete("/comments/{comment_id}", response_model=CommentSchema)
def remove_comment(comment_id: str, db: Session = Depends(get_db)):
    comment_to_remove = db.get(CommentORM, comment_id)
    db.delete(comment_to_remove)
    db.commit()
    return {"status": "success", "message": "Комментарий успешно удален"}


@app.patch("/comments/{comment_id}", response_model=CommentSchema)
def change_comment(payload: UpdateCommentSchema, comment_id: str, db: Session = Depends(get_db)):
    comment_to_update = db.get(CommentORM, comment_id)
    if payload.author is not None:
        comment_to_update.author = payload.author
    if payload.text is not None:
        comment_to_update.text = payload.text
    db.commit()
    db.refresh(comment_to_update)
    return comment_to_update

