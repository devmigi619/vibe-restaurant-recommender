import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="jeju_restaurants")


def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def add_restaurant(restaurant: dict):
    """식당 데이터를 벡터 DB에 저장 (중복이면 덮어씀)"""
    vibe_text = restaurant.get("vibe_description", "")
    embedding = embed_text(vibe_text)

    collection.upsert(
        ids=[restaurant["id"]],
        embeddings=[embedding],
        documents=[vibe_text],
        metadatas=[{
            "name": restaurant["name"],
            "address": restaurant.get("address", ""),
            "category": restaurant.get("category", ""),
            "phone": restaurant.get("phone", ""),
            "url": restaurant.get("url", ""),
            "vibe_tags": restaurant.get("vibe_tags", ""),
        }]
    )


def clear_collection():
    """컬렉션 전체 삭제 후 재생성"""
    global collection
    chroma_client.delete_collection(name="jeju_restaurants")
    collection = chroma_client.get_or_create_collection(name="jeju_restaurants")


def search_restaurants(vibe_description: str, n_results: int = 5) -> list[dict]:
    """감성 설명으로 유사한 식당 검색"""
    embedding = embed_text(vibe_description)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    restaurants = []
    for i, metadata in enumerate(results["metadatas"][0]):
        restaurants.append({
            **metadata,
            "vibe_description": results["documents"][0][i],
            "similarity_score": 1 - results["distances"][0][i]
        })
    return restaurants


def get_restaurant_count() -> int:
    return collection.count()
