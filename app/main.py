from fastapi import FastAPI
from .database import Base, engine
from .routers import client
from . import models


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(client.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Reservation System"}

