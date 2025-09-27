from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.db.session import engine
from app.db.models import Base

def create_tables():
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Supportive Communication Agent API",
    description="An API to assist children with autism in communication.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(api_router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Supportive Communication Agent API"}
