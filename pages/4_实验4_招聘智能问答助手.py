

import streamlit as st
st.set_page_config(page_title="招聘智能助手")

import pandas as pd
import json
import os
from utils.glm import init_glm_ai, ask_glm
from utils.functions import get_skill_distribution, get_recommend_jobs, get_skill_requirements

MEMORY_FILE = "chat_history.json"

def save_message(message):
    history = load_history()
    history.append(message)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def clear_history():
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

@st.cache_data
def load_dataset():
    return pd.read_csv("data/招聘数据集(含技能列表）.csv")

dataset = load_dataset()

# 注册函数
function_list = {
    "get_skill_distribution": get_skill_distribution,
    "get_recommend_jobs": get_recommend_jobs,
    "get_skill_requirements": get_skill_requirements
}

# 注册 tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_skill_distribution",
            "description": "获取技能对应的热门岗位",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommend_jobs",
            "description": "根据关键词推荐相关岗位信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_skill_requirements",
            "description": "分析岗位常见技能",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"}
                },
                "required": ["keyword"]
            }
        }
    }
]

# 🎛️ 侧边栏配置
with st.sidebar:
    st.title("招聘智能助手设置")
    key = st.text_input("请输入 API Token:", type="password")
    if key:
        st.success("✅ API Token 已配置")
    else:
        st.warning("⚠️ 请先输入 API Token")

    model = st.selectbox("选择模型", ["glm", "glm-4"])
    temperature = st.slider("temperature", 0.0, 1.5, 0.7)
    chart_type = st.selectbox("选择可视化图像类型", ["条形图", "饼图", "表格"])
    st.session_state["chart_type"] = chart_type

    if st.button("清空聊天记录"):
        clear_history()
        st.session_state.messages = [{"role": "assistant", "content": "你好，我是招聘智能助手，有什么可以帮您？"}]

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = load_history()
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "你好，我是招聘智能助手，有什么可以帮您？"}]

# 展示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image"):
            st.image(msg["image"], use_container_width=True)
        if msg.get("table"):
            st.dataframe(pd.DataFrame(msg["table"]))

# 主对话逻辑
if key and (prompt := st.chat_input("请输入您的问题...")):
    api_key = init_glm_ai(key)

    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    save_message(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("分析中..."):

            skill_keywords = ["C++", "Java", "Python", "嵌入式", "算法", "Go", "测试", "前端", "后端"]
            matched_skill = next((kw for kw in skill_keywords if kw.lower() in prompt.lower()), None)

            # 自动功能触发
            if "可以从事什么岗位" in prompt and matched_skill:
                result = get_skill_distribution(dataset, skill=matched_skill, chart_type=st.session_state["chart_type"])

            elif "需要什么技能" in prompt and matched_skill:
                result = get_skill_requirements(dataset, keyword=matched_skill)

            elif "推荐" in prompt and matched_skill:
                result = get_recommend_jobs(dataset, keyword=matched_skill)

            else:
                result = ask_glm(
                    api_key,
                    tools=tools,
                    temperature=temperature,
                    content=prompt,
                    function_list=function_list,
                    dataset=dataset,
                    chart_type=st.session_state.get("chart_type", "饼图")
                )

            # 渲染输出
            if isinstance(result, dict) and "text" in result:
                st.markdown(result["text"])
                if result.get("plot"):
                    st.image(result["plot"], use_container_width=True)
                if isinstance(result.get("table"), pd.DataFrame):
                    st.dataframe(result["table"])

                assistant_msg = {
                    "role": "assistant",
                    "content": result["text"],
                    "image": result.get("plot"),
                    "table": result.get("table").to_dict() if isinstance(result.get("table"), pd.DataFrame) else None
                }
                st.session_state.messages.append(assistant_msg)
                save_message(assistant_msg)

            else:
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})
                save_message({"role": "assistant", "content": result})
