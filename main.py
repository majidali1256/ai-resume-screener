from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "AI Resume Screener & Feedback System",
        "message": "Welcome! The backend API is running successfully."
    }