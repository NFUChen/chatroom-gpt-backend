import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct, UpdateStatus
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import get_current_datetime


import openai
from openai.embeddings_utils import get_embedding

openai.api_key = "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"
embedding_model = "text-embedding-ada-002"

class QdrantVectorStore:
    def __init__(self,
                 host: str = "qdrant",
                 port: int = 6333,
                 vector_size: int = 1536,
                 vector_distance: str=Distance.COSINE,
                 text_spliter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
                            chunk_size = 500,
                            chunk_overlap  = 50,
                            length_function = len,
                            add_start_index = True,
                        )
                 ) -> None:

        self.client = QdrantClient(
            url=host,
            port=port,
        )

        self.vector_size = vector_size
        self.vector_distance = vector_distance
        self.text_spliter = text_spliter

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

    def upsert_text(self, collection_name: str, text: str) -> str:
        if len(text) == 0:
            raise ValueError("Entering empty text, abort upsert text request")

        if not self._is_collection_exist(collection_name):
            self._set_up_collection(collection_name)
        document_id = str(uuid.uuid4())
        text_chunks = self.text_spliter.split_text(text)

        points = []
        embeddings = []
        for chunk in text_chunks:
            text_vector = get_embedding(chunk, engine=embedding_model)
            print(f"Create embedding for chunk text: {chunk}\n\n")
            chunk_id = str(uuid.uuid4())
            payload_dict = {
                "text": chunk, 
                "updated_at": get_current_datetime(), 
                "document_id": document_id,
            }
            # document id is to identification purpose
            # chunk id is for updating purpose
            embeddings.append(
                {**payload_dict, "vector": text_vector, "chunk_id": chunk_id }
            )
            point = PointStruct(id=chunk_id, vector=text_vector, payload=payload_dict)
            points.append(point)

        operation_info = self.client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )

        if operation_info.status == UpdateStatus.COMPLETED:
            print("Text inserted successfully!")
        else:
            print("Failed to insert Text")

        return {
            "collection_name": collection_name,
            "points": embeddings,
            "status": operation_info.status
        }

    def search_text_chunks(self, collection_name: str, input_query: str, limit: int = 5, threshold: float = 0.8) -> list[dict[str, str]]:
        if len(input_query) == 0:
            print("Empty query is forbidden, returning a empty result")
            return []
        
        if len(input_query) > 3000:
            print("Input query too large, returning a empty result")
            return []
        
        if not self._is_collection_exist(collection_name):
            print(f"Collection: {collection_name} not exist yet, set up a collection")
            self._set_up_collection(collection_name)
            return []

        input_vector = get_embedding(input_query, engine=embedding_model)
        payloads = self.client.search(
            collection_name=collection_name,
            query_vector=input_vector,
            limit=limit
        )

        result = []
        for item in payloads:
            if item.score < threshold:
                print(f"{item.score} is lower than {threshold}, try higher for includ this document: {item.payload}")
                continue
            data = {
                # "id": item.id, 
                "similarity_score": item.score, 
                "text": item.payload["text"], 
                "updated_at": item.payload["updated_at"], 
                "document_id": item.payload["document_id"]
            }
            result.append(data)
        return result
    
qdrant_vector_store = QdrantVectorStore()