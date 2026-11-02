
import re

from app.retrieval.service import HybridRetriever
from app.rag.context import select_context, format_context
from app.rag.models import ChatResponse
from app.rag.prompts import SYSTEM_PROMPT
from app.ollama_client import client, CHAT_MODEL
from pydantic import BaseModel, Field
from app.rag.models import AnswerStatus


INSUFFICIENT_EVIDENCE = (
    "I couldn't find enough information in my current "
    "lore sources to answer that confidently."
)

class GeneratedAnswer(BaseModel):
    status: AnswerStatus
    answer: str = Field(min_length=1)


class RAGService:
    def __init__(self):
        self.retriever = HybridRetriever(
            candidate_limit=20,
            rrf_k=60,
        )

    def answer(self, question: str) -> ChatResponse:
        question = question.strip()

        if not question:
            return ChatResponse(
                answer="Please enter a question.",
                grounded=False,
            )

        # 1. Retrieve relevant lore passages.
        results = self.retriever.search(
            query=question,
            limit=10,
        )

        # 2. Select context passages.
        sources = select_context(
            results,
            max_chunks=4,
            max_per_document=2,
        )

        if not sources:
            return ChatResponse(
                answer=INSUFFICIENT_EVIDENCE,
                grounded=False,
            )

        # 3. Format numbered source passages.
        context = format_context(sources)

        # 4. Create the user message.
        user_prompt = (
            "Use the following retrieved lore passages "
            "to answer the question.\n\n"
            f"<context>\n{context}\n</context>\n\n"
            f"Question: {question}\n\n"
            "Answer with citations to the context. "
            "If the evidence is insufficient, say so."
        )

        # 5. Generate the answer locally.
        response = client.chat(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=GeneratedAnswer.model_json_schema(),
            options={
                "temperature": 0.1,
                "num_ctx": 8192,
                "num_predict": 1200,
            },
        )

        generated = GeneratedAnswer.model_validate_json(
            response.message.content or ""
        )

        if generated.status == AnswerStatus.INSUFFICIENT_EVIDENCE:
            return ChatResponse(
                answer=generated.answer,
                sources=[],
                status=AnswerStatus.INSUFFICIENT_EVIDENCE,
                grounded=False,
            )

        answer = generated.answer

        cited_ids = {
            int(number)
            for number in re.findall(r"\[(\d+)\]", answer)
        }

        valid_ids = {source.id for source in sources}

        if not cited_ids or not cited_ids.issubset(valid_ids):
            return ChatResponse(
                answer=INSUFFICIENT_EVIDENCE,
                sources=[],
                status=AnswerStatus.INSUFFICIENT_EVIDENCE,
                grounded=False,
            )

        return ChatResponse(
            answer=answer,
            sources=[
                source for source in sources
                if source.id in cited_ids
            ],
            status=generated.status,
            grounded=True,
        )

