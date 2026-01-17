from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, reports, analytics, votes

app = FastAPI(title="Citizen AI System API")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3005",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3005",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(votes.router)
app.include_router(analytics.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Citizen AI System Backend is running"}
