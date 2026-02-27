"""Main FastAPI app"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}
