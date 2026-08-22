from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, sessionmaker, mapped_column, Session
from pydantic import BaseModel
from uuid import uuid4
from contextlib import asynccontextmanager


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/news_db"

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class PostORM(Base):
    __tablename__ = "posts"

    title: Mapped[str]
    content: Mapped[str]


class PostCreateSchema(BaseModel):
    title: str
    content: str

class PostSchema(BaseModel):
    id: str
    title: str
    content: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.post("/posts", status_code=201, response_model=PostSchema)
def create_post(payload: PostCreateSchema, db: Session = Depends(get_db)):
    new_post = PostORM(title=payload.title, content=payload.content)
    db.add(new_post)
    db.commit()
    return new_post

@app.get("/posts", response_model=list[PostSchema])
def read_posts(db: Session = Depends(get_db)):
    posts_from_db = db.scalars(select(PostORM)).all()
    return posts_from_db

