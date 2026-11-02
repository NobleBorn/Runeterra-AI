
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import Field
from app.retrieval.service import HybridRetriever
from app.retrieval.models import SearchResponse
from app.rag.models import ChatRequest, ChatResponse
from app.rag.service import RAGService
from fastapi.responses import StreamingResponse
from app.rag.streaming import stream_rag_answer

app = FastAPI(
    title="Runeterra AI API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Runeterra AI backend is running"
    }



rag_service = RAGService()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return rag_service.answer(request.message)


retriever = HybridRetriever()


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=1000,
    )
    limit: int = Field(default=5, ge=1, le=20)


@app.post("/search", response_model=SearchResponse)
def search_lore(request: SearchRequest):
    results = retriever.search(
        query=request.query,
        limit=request.limit,
    )

    return SearchResponse(
        query=request.query,
        results=results,
    )


@app.post("/chat/stream")
async def chat_stream(
    body: ChatRequest,
    request: Request,
):
    return StreamingResponse(
        stream_rag_answer(
            question=body.message,
            request=request,
            history=body.history,
        ),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Content-Type-Options": "nosniff",
        },
    )
