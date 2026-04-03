import os

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler as LangfuseCallbackHandler

from tools import analyze_image_vibe, search_matching_restaurants, set_current_image

load_dotenv()

# 환경 설정 (local, local-docker, server)
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

# thinking 비활성화 시 temperature=0.6 고정 (Kimi K2.5 공식 스펙)
_llm = ChatOpenAI(
    model="kimi-k2.5",
    openai_api_key=os.getenv("MOONSHOT_API_KEY"),
    openai_api_base="https://api.moonshot.ai/v1",
    temperature=0.6,
)
llm = _llm.bind(extra_body={"thinking": {"type": "disabled"}})

tools = [analyze_image_vibe, search_matching_restaurants]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)


def run_vibe_recommendation(image_base64: str) -> dict:
    """이미지를 받아 감성 맛집을 추천하는 메인 함수"""
    set_current_image(image_base64)

    langfuse_handler = LangfuseCallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        tags=[ENVIRONMENT],  # 환경 태그 추가
    )

    result = agent_executor.invoke(
        {
            "input": (
                "업로드된 이미지의 감성과 분위기를 분석한 후, "
                "그 감성에 어울리는 제주 맛집을 추천해주세요. "
                "먼저 이미지를 분석하고, 그 결과로 맛집을 검색한 뒤, "
                "최종적으로 왜 이 맛집들이 어울리는지 한국어로 친절하게 설명해주세요."
            )
        },
        config={"callbacks": [langfuse_handler]},
    )

    return {
        "output": result["output"],
        "intermediate_steps": [
            {
                "tool": step[0].tool,
                "input": step[0].tool_input,
                "output": step[1],
            }
            for step in result.get("intermediate_steps", [])
        ],
    }
