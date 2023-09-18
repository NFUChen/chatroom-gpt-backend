from openai.embeddings_utils import get_embedding
from dataclasses import dataclass
from utils import get_current_datetime
import uuid
import requests
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
        self.query_api = f"http://query_manager:5000/query"
    def get_embedding(self, text: str, document_id: str, _hash: str | None = None) -> Embedding:
        text_vector = get_embedding(text, engine= self.MODEL)
        return Embedding(
            document_id= document_id,
            chunk_id= str(uuid.uuid4()),
            text= text,
            text_hash= _hash,
            updated_at= get_current_datetime(),
            vector= text_vector
        )
    
    def get_adjancent_embeddings(self, document_id: str,chunk_id: str) -> tuple[dict[str, str]]:
        '''
        Target chunk is not included
        '''

        sql = f'''
        WITH TargetEmbedding AS (
            SELECT embedding_id
            FROM embeddings
            WHERE chunk_id = '{chunk_id}'
        )
        SELECT document_id, chunk_id, text, updated_at
        FROM embeddings
        WHERE (
            (embedding_id = (SELECT embedding_id FROM TargetEmbedding) - 1 OR
            embedding_id = (SELECT embedding_id FROM TargetEmbedding) + 1)
        ) 
        AND document_id = '{document_id}'
        '''
        post_json = {
            "query": sql
        }

        return requests.post(
            self.query_api, json= post_json
        ).json()["data"]

embedding_service = EmbeddingService()