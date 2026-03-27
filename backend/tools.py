import base64
from openai import OpenAI
from langchain.tools import tool
from vector_store import search_restaurants
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 이미지 데이터를 에이전트에게 전달하기 위한 전역 컨텍스트
_current_image_base64: str = ""


def set_current_image(image_base64: str):
    global _current_image_base64
    _current_image_base64 = image_base64


@tool
def analyze_image_vibe(dummy: str = "") -> str:
    """업로드된 이미지를 분석해서 감성과 분위기를 설명합니다. 항상 첫 번째로 호출하세요."""
    if not _current_image_base64:
        return "이미지가 없습니다."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{_current_image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """이 이미지의 감성과 분위기를 분석해주세요.
어떤 날씨인지, 어떤 기분이 드는지, 어떤 상황인지를 포함해서
맛집 추천에 활용할 수 있도록 구체적으로 설명해주세요. (한국어, 3-4문장)"""
                    }
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()


@tool
def search_matching_restaurants(vibe_description: str) -> str:
    """감성 설명을 받아 분위기가 맞는 제주 맛집을 검색합니다. analyze_image_vibe 결과를 입력으로 사용하세요."""
    results = search_restaurants(vibe_description, n_results=5)

    if not results:
        return "검색 결과가 없습니다. 데이터 파이프라인을 먼저 실행해주세요."

    output = []
    for i, r in enumerate(results, 1):
        output.append(
            f"{i}. {r['name']}\n"
            f"   주소: {r['address']}\n"
            f"   카테고리: {r['category']}\n"
            f"   감성: {r['vibe_description']}\n"
            f"   전화: {r.get('phone', '정보 없음')}\n"
            f"   링크: {r.get('url', '')}"
        )
    return "\n\n".join(output)
