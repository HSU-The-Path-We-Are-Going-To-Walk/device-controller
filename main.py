from fastapi import FastAPI
from routers import button, vision

app = FastAPI()
app.include_router(button.router)
# app.include_router(vision.router)