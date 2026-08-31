from contextlib import asynccontextmanager

from fastapi import FastAPI
from netops_ingestion.services.factory import create_knowledge_base_service

from net_tools_app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.knowledge_base = create_knowledge_base_service(embedding_model="Qwen/Qwen3-Embedding-0.6B", collection_name="netops_kb", persist_directory="../net-ops-kb-rag/storage/chroma")
    yield

app = FastAPI(title="Network Operations Tools API app", version="0.1.0", lifespan=lifespan)

app.include_router(router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

