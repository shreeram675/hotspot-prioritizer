from fastapi import FastAPI
from .routers import auth, reports, hotspots, admin, analytics
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Neighborhood Hotspot Prioritizer")

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(reports.router)
app.include_router(hotspots.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Neighborhood Hotspot Prioritizer API"}
