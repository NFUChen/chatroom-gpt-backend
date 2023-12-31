from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct, UpdateStatus
from embedding_service import Embedding


class QdrantVectorStore:
    def __init__(self,
                 host: str = "qdrant",
                 port: int = 6333,
                 vector_size: int = 1536,
                 vector_distance: str=Distance.COSINE,
                 ) -> None:
        
        self.client = QdrantClient(
            url=host,
            port=port,
        )

        self.vector_size = vector_size
        self.vector_distance = vector_distance

    def _set_up_collection(self, collection_name: str) -> None:
        
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=self.vector_size, 
                distance=self.vector_distance
            )
        )

    def _is_collection_exist(self, collection_name: str) -> bool:
        try:
            self.client.get_collection(collection_name=collection_name)
            return True
        except Exception as error:
            return False

    def upsert_text(self, collection_name: str, embeddings:list[Embedding]) -> dict[str, str | list[Embedding]]:

        if not self._is_collection_exist(collection_name):
            self._set_up_collection(collection_name)
        points = [
            PointStruct(
                id=embedding.chunk_id, # chunk id is here
                vector= embedding.vector, 
                payload={
                            "text": embedding.text, 
                            "updated_at": embedding.updated_at, 
                            "document_id": embedding.document_id
                        }
            ) for embedding in embeddings
        ]
        operation_info = self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        is_ok = operation_info.status == UpdateStatus.COMPLETED

        return {
            "is_ok": is_ok,
            "collection_name": collection_name,
            "embeddings": embeddings
        }

    def search_text_chunks(self, collection_name: str, embedding: Embedding, limit: int = 5, threshold: float = 0.8) -> list[dict[str, str]]:
        if not self._is_collection_exist(collection_name):
            print(f"Collection: {collection_name} not exist yet, set up a collection")
            self._set_up_collection(collection_name)
            return []

        payloads = self.client.search(
            collection_name=collection_name,
            query_vector=embedding.vector,
            limit=limit,
            score_threshold= threshold
        )
        return [{
                "chunk_id": item.id, # chunk id is here
                "similarity_score": item.score, 
                "text": item.payload["text"], 
                "updated_at": item.payload["updated_at"], 
                "document_id": item.payload["document_id"],
            } for item in payloads]
    
qdrant_vector_store = QdrantVectorStore()