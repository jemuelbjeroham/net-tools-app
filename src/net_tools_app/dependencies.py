from fastapi import Request
from netops_ingestion.services.knowledge_base_service import KnowledgeBaseService


def get_knowledge_base(request: Request) -> KnowledgeBaseService:
    return request.state.knowledge_base
