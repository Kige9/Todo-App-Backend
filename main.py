from fastapi import FastAPI, status, Response, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase, Session
from contextlib import asynccontextmanager


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool

class TaskCreateSchema(BaseModel):
    title: str

class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None

tasks: list[TaskSchema] = []
book: str = ""

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(id=task_orm.id, title=task_orm.title, completed=task_orm.completed)

class BookCreateSchema(BaseModel):
    book: str

@app.post("/book")
def set_book(payload: BookCreateSchema):
    global book
    book = payload.book
    return {"message": "Книга сохранена"}

@app.get("/book")
def get_book():
    return f"Любимая книга: {book}"

@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    task_for_update = db.get(TaskORM, task_id)
    if payload.title:
        task_for_update.title = payload.title
    if payload.completed:
        task_for_update.completed = payload.completed
    db.commit()
    return task_for_update

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id, db: Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()


class CategoriesORM(Base):
    __tablename__ = "categories"

    name: Mapped[str]
class CategoriesSchema(BaseModel):
    id: str
    name: str

    class config:
        from_attributes = True

class CategoriesCreateSchema(BaseModel):
    name: str

class CategoriesUpdateSchema(BaseModel):
    name: str | None = None



@app.get("/categories", response_model=list[CategoriesSchema])
def get_categories(db: Session = Depends(get_db)):
    all_categories = db.scalars(select(CategoriesORM)).all()
    return all_categories


@app.post("/categories", status_code=status.HTTP_201_CREATED)
def add_category(payload: CategoriesCreateSchema, db: Session = Depends(get_db)):
    new_category = CategoriesORM(name=payload.name)
    db.add(new_category)
    db.commit()
    return new_category


@app.patch("/categories/{category_id}")
def update_category(payload: CategoriesCreateSchema, category_id: str, db: Session = Depends(get_db)):
    category_to_update = db.get(CategoriesORM, category_id)
    if payload.name is not None:
        category_to_update.name = payload.name
    db.commit()
    return category_to_update


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def category_to_delete(category_id: str, db: Session = Depends(get_db)):
    category_to_del = db.get(CategoriesORM, category_id)
    db.delete(category_to_del)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)