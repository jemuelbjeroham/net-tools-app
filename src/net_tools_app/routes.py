from fastapi import APIRouter, Depends
from netops_ingestion.services.knowledge_base_service import KnowledgeBaseService

from net_tools_app.dependencies import get_knowledge_base
from net_tools_app.schemas import SearchRequest, SearchResponse, SearchResult

router = APIRouter()

@router.post("/api/v1/search", response_model=SearchResponse)
def search_knowledge(request: SearchRequest, knowledge_base: KnowledgeBaseService = Depends(get_knowledge_base)) -> SearchResponse:
    results = knowledge_base.search(query=request.query, top_k=request.top_k)

    return SearchResponse(
        results=[
            SearchResult(
                content=result.content,
                source=str(result.source),
                chunk_index=result.chunk_index,
                metadata=result.metadata,
            )
            for result in results
        ]
    )