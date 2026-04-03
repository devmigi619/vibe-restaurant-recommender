import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
from agent import run_vibe_recommendation
from vector_store import get_restaurant_count, clear_collection
from data_pipeline import run_pipeline
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="제주 감성 맛집 추천 API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "restaurant_count": get_restaurant_count()
    }


@app.post("/init-data")
def init_data():
    """카카오 API로 맛집 데이터 수집 및 벡터 DB 저장 (최초 1회 실행)"""
    if get_restaurant_count() > 0:
        return {
            "message": f"이미 {get_restaurant_count()}개 식당이 저장되어 있습니다.",
            "count": get_restaurant_count()
        }
    try:
        run_pipeline()
        return {
            "message": "데이터 초기화 완료",
            "count": get_restaurant_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset-data")
def reset_data():
    """DB 초기화 후 데이터 재수집"""
    clear_collection()
    run_pipeline()
    return {"message": "리셋 완료", "count": get_restaurant_count()}


@app.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    """이미지를 받아 감성 맛집 추천"""
    if get_restaurant_count() == 0:
        raise HTTPException(
            status_code=400,
            detail="맛집 데이터가 없습니다. /init-data를 먼저 실행해주세요."
        )

    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")

    try:
        result = run_vibe_recommendation(image_base64)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
