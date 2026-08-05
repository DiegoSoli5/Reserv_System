from fastapi import FastAPI
from .database import Base, engine
from .routers import client, auth, event, booking
from . import models


# Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(client.router)
app.include_router(auth.router)
app.include_router(event.router)
app.include_router(booking.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Reservation System"}

