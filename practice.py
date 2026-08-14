from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

posts: list[dict] = []

class PostSchema(BaseModel):
    title: str
    content: str

@app.post("/posts")
def create_post(payload: PostSchema):
    new_post = {
        "id": len(posts) + 1,
        "title": payload.title,
        "content": payload.content
    }
    posts.append(new_post)
    return f"Пост успешно добавлен {new_post}"

@app.get("/posts")
def get_posts():
    return f"Все посты: {posts}"

