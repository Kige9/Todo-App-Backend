from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
from uuid import uuid4
from contextlib import asynccontextmanager



DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/shop_db"
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(bind=engine)



class BaseShopORM(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))


class ProductORM(BaseShopORM):
    __tablename__ = "products"

    name: Mapped[str]
    price: Mapped[int]
    quantity: Mapped[int]



class ProductSchema(BaseModel):
    id: str
    name: str
    price: int
    quantity: int

    class Config:
        from_attributes = True

class ProductCreateSchema(BaseModel):
    name: str
    price: int
    quantity: int



def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    BaseShopORM.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)



@app.post("/products", response_model=ProductSchema)
def create_product(payload: ProductCreateSchema, db: Session = Depends(get_db)):
    new_product = ProductORM(name=payload.name, price=payload.price, quantity=payload.quantity)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    all_products = db.scalars(select(ProductORM)).all()
    return all_products


@app.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product_to_delete = db.get(ProductORM, product_id)
    db.delete(product_to_delete)
    db.commit()


@app.patch("/products/{product_id}", response_model=ProductCreateSchema)
def product_to_change(payload: ProductCreateSchema, product_id: str, db: Session = Depends(get_db)):
    product_to_change = db.get(ProductORM, product_id)
    product_to_change.name = payload.name
    product_to_change.quantity = payload.quantity
    product_to_change.price = payload.price
    db.commit()
    return product_to_change


