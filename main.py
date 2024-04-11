import asyncio

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import uvicorn

from routes.login import loginroute
from routes.todos import todosroute
from routes.admin import adminrouter
from db.database import init_models

app = FastAPI()


app.include_router(loginroute, prefix="/auth")
app.include_router(todosroute, prefix="/todo")
app.include_router(adminrouter, prefix="/admin")


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


@app.get("/")
async def index():
    return "Todo list API"


if __name__ == "__main__":
    asyncio.run(init_models())
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, workers=3, reload=True)
