from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from signal import get_latest_signal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/signal/latest")
def latest():
    return get_latest_signal()
