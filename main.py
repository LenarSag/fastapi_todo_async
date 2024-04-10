import asyncio

from fastapi import FastAPI
import uvicorn

from routes.login import loginroute
from routes.todos import todosroute
from db.database import init_models

app = FastAPI()

app.include_router(loginroute, prefix="/auth")
app.include_router(todosroute, prefix="/todo")


@app.get("/")
async def index():
    return "Todo list API"


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, workers=3, reload=True)
