import openai
from openai.embeddings_utils import get_embedding
from dataclasses import dataclass
from utils import get_current_datetime


openai.api_key = "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"


@dataclass
class Embedding:
    document_id: str
    chunk_id: str
    text: str
    text_hash: str | None
    updated_at: str
    vector: list[float]

    def to_dict(self) -> dict[str, str | list[float]]:
        return self.__dict__


class EmbeddingService:    
    MODEL = "text-embedding-ada-002"
    def __init__(self) -> None:
        ...
    def get_embedding(self, text: str, document_id: str, _hash: str | None = None) -> Embedding:
        text_vector = get_embedding(text, engine= self.MODEL)
        return Embedding(
            document_id= document_id,
            chunk_id= document_id,
            text= text,
            text_hash= _hash,
            updated_at= get_current_datetime(),
            vector= text_vector
        )

embedding_service = EmbeddingService()