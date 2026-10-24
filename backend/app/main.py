
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="ResumeAI",
    description="AI Resume Tailoring and Learning Roadmap Agent",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "ResumeAI backend is running!",
        "status": "success",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
