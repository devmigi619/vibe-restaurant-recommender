from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "jeju_restaurants"
VECTOR_SIZE = 1536  # text-embedding-3-small 출력 차원


def _ensure_collection():
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
    except Exception:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


_ensure_collection()


def embed_text(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def add_restaurant(restaurant: dict):
    """식당 데이터를 벡터 DB에 저장 (중복이면 덮어씀)"""
    vibe_text = restaurant.get("vibe_description", "")
    embedding = embed_text(vibe_text)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=int(restaurant["id"]),
                vector=embedding,
                payload={
                    "name": restaurant["name"],
                    "address": restaurant.get("address", ""),
                    "category": restaurant.get("category", ""),
                    "phone": restaurant.get("phone", ""),
                    "url": restaurant.get("url", ""),
                    "vibe_description": vibe_text,
                },
            )
        ],
    )


def clear_collection():
    """컬렉션 전체 삭제 후 재생성"""
    qdrant_client.delete_collection(COLLECTION_NAME)
    _ensure_collection()


def search_restaurants(vibe_description: str, n_results: int = 5) -> list[dict]:
    """감성 설명으로 유사한 식당 검색"""
    embedding = embed_text(vibe_description)
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=n_results,
    )

    return [
        {
            **hit.payload,
            "similarity_score": hit.score,
        }
        for hit in results
    ]


def get_restaurant_count() -> int:
    try:
        return qdrant_client.count(collection_name=COLLECTION_NAME).count
    except Exception:
        return 0
