from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from tools import analyze_image_vibe, search_matching_restaurants, set_current_image
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [analyze_image_vibe, search_matching_restaurants]

# LangChain Hub에서 ReAct 프롬프트 가져오기
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)


def run_vibe_recommendation(image_base64: str) -> dict:
    """이미지를 받아 감성 맛집을 추천하는 메인 함수"""
    set_current_image(image_base64)

    result = agent_executor.invoke({
        "input": (
            "업로드된 이미지의 감성과 분위기를 분석한 후, "
            "그 감성에 어울리는 제주 맛집을 추천해주세요. "
            "먼저 이미지를 분석하고, 그 결과로 맛집을 검색한 뒤, "
            "최종적으로 왜 이 맛집들이 어울리는지 친절하게 설명해주세요."
        )
    })

    return {
        "output": result["output"],
        "intermediate_steps": [
            {
                "tool": step[0].tool,
                "input": step[0].tool_input,
                "output": step[1]
            }
            for step in result.get("intermediate_steps", [])
        ]
    }
