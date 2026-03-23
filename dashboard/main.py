from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dashboard.routes import router
import uvicorn
import os

app = FastAPI(
    title="Thinguva Sentinel",
    description="Agent Governance & Reliability Platform",
    version="0.1.0"
)

app.include_router(router, prefix="/api")

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/health")
def health():
    return {"status": "running", "product": "Thinguva Sentinel", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("dashboard.main:app", host="0.0.0.0", port=8000, reload=True)