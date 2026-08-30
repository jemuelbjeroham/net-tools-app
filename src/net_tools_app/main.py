from fastapi import FastAPI

app = FastAPI(title="Network Operations Tools API app", version="0.1.0")

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

