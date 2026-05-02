import os
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import notas
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sales Service")

app.include_router(notas.router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sales-service",
        "environment": os.getenv("ENVIRONMENT", "local")
    }
