import openai
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai.embeddings_utils import get_embedding
from dataclasses import dataclass
from utils import get_current_datetime
import hashlib

DEFAULT_SPLITER = RecursiveCharacterTextSplitter(
    chunk_size = 500, chunk_overlap  = 50, length_function = len, add_start_index = True
)

openai.api_key = "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"


@dataclass
class Embedding:
    document_id: str
    chunk_id: str
    text: str
    text_hash: str
    updated_at: str
    vector: list[float]

    def to_dict(self) -> dict[str, str | list[float]]:
        return self.__dict__



class EmbeddingService:    
    MODEL = "text-embedding-ada-002"
    def __init__(self, text_spliter: RecursiveCharacterTextSplitter) -> None:
        self.text_spliter = text_spliter

    def __get_hash(self, string: str) -> str:
        return hashlib.sha256(string.encode("utf-8")).hexdigest()

    def get_embedding(self, text: str) -> Embedding:
        document_id = str(uuid.uuid4())
        text_vector = get_embedding(text, engine= self.MODEL)
        return Embedding(
            document_id= document_id,
            chunk_id= document_id,
            text= text,
            text_hash= self.__get_hash(text),
            updated_at= get_current_datetime(),
            vector= text_vector
        )
    
    def get_embedding_list(self, text: str) -> list[Embedding]:
        document_id = str(uuid.uuid4())
        text_chunks = self.text_spliter.split_text(text)
        embeddings = []
        for chunk in text_chunks:
            text_vector = get_embedding(chunk, engine= self.MODEL)
            print(f"Create embedding for chunk text: {chunk}\n\n")
            embedding = Embedding(
                document_id= document_id, 
                chunk_id= str(uuid.uuid4()), 
                text= chunk, 
                text_hash= self.__get_hash(chunk),
                updated_at= get_current_datetime(), 
                vector= text_vector
            )
            # document id is to identification purpose
            # chunk id is for updating purpose
            embeddings.append(embedding)
        return embeddings

embedding_service = EmbeddingService(text_spliter= DEFAULT_SPLITER)