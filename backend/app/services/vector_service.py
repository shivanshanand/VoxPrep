from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

class VectorService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = "interview_questions"
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Create collection if doesn't exist"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        except Exception:
            pass  # Collection already exists
    
    async def store_question(self, question_id: str, text: str, metadata: dict, embedding: list):
        """Store question with embedding"""
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=question_id,
                    vector=embedding,
                    payload={"text": text, **metadata}
                )
            ]
        )
    
    async def search_similar_questions(self, query_embedding: list, filters: dict, limit: int = 5):
        """Find similar questions based on role/experience"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filters,
            limit=limit
        )
        return results

vector_service = VectorService()
