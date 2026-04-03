import os
import time

from dotenv import load_dotenv
from openai import OpenAI
import requests

from vector_store import add_restaurant, get_restaurant_count

load_dotenv()

kakao_key = os.getenv("KAKAO_REST_API_KEY")

moonshot_client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1",
)

JEJU_KEYWORDS = [
    "제주 흑돼지",
    "제주 해산물",
    "제주 고기국수",
    "제주 카페",
    "서귀포 맛집",
    "제주시 맛집",
    "제주 해녀",
    "제주 갈치",
    "제주 한식",
    "제주 이색 맛집",
]


def fetch_restaurants_by_keyword(keyword: str, max_pages: int = 3) -> list[dict]:
    """카카오 API로 키워드 기반 식당 검색"""
    headers = {"Authorization": f"KakaoAK {kakao_key}"}
    restaurants = []
    seen_ids = set()

    for page in range(1, max_pages + 1):
        params = {
            "query": keyword,
            "category_group_code": "FD6",
            "size": 15,
            "page": page,
        }
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers=headers,
            params=params,
        )
        data = response.json()
        places = data.get("documents", [])
        if not places:
            break

        for place in places:
            if place["id"] not in seen_ids:
                seen_ids.add(place["id"])
                restaurants.append({
                    "id": place["id"],
                    "name": place["place_name"],
                    "address": place.get("road_address_name") or place.get("address_name", ""),
                    "category": place.get("category_name", ""),
                    "phone": place.get("phone", ""),
                    "url": place.get("place_url", ""),
                })

        if data.get("meta", {}).get("is_end", True):
            break
        time.sleep(0.1)

    return restaurants


def generate_vibe_description(restaurant: dict) -> str:
    """Kimi K2.5로 식당의 감성 설명 생성"""
    prompt = f"""다음 식당의 감성과 분위기를 한국어로 자세히 설명해주세요.
어떤 날씨, 기분, 상황에 어울리는지, 어떤 사람들이 오면 좋을지 포함해서 2-3문장으로 작성해주세요.

식당명: {restaurant['name']}
카테고리: {restaurant['category']}
주소: {restaurant['address']}

감성 설명:"""

    response = moonshot_client.chat.completions.create(
        model="kimi-k2.5",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"thinking": {"type": "disabled"}},
    )
    return response.choices[0].message.content.strip()


def run_pipeline():
    """전체 데이터 파이프라인 실행"""
    print("카카오 API로 제주 맛집 수집 시작...")
    all_restaurants = []
    seen_ids = set()

    for keyword in JEJU_KEYWORDS:
        print(f"  검색 중: {keyword}")
        restaurants = fetch_restaurants_by_keyword(keyword)
        for r in restaurants:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                all_restaurants.append(r)
        time.sleep(0.3)

    total = len(all_restaurants)
    print(f"총 {total}개 식당 수집 완료")
    print(f"Kimi K2.5로 감성 설명 순차 생성 중... (1초 간격)")

    for i, restaurant in enumerate(all_restaurants, 1):
        try:
            vibe = generate_vibe_description(restaurant)
            restaurant["vibe_description"] = vibe
            add_restaurant(restaurant)
            print(f"  [{i}/{total}] ✓ {restaurant['name']}")
        except Exception as e:
            print(f"  [{i}/{total}] ❌ {restaurant['name']}: {e}")
        time.sleep(1)

    print(f"완료! 벡터 DB에 {get_restaurant_count()}개 저장됨")


if __name__ == "__main__":
    run_pipeline()
