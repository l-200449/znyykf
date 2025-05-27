import streamlit as st
st.set_page_config(page_title="实验3 - 技术关联性挖掘", page_icon="🔍")

import pandas as pd
from utils.skill_util import (
    get_asso_skill,
    cacu_skill_position_wordcount,
    cacu_postion_skill_wordcount,
)
from utils.glm import init_glm_ai
from utils.tools import tools

# 📊 侧边栏配置
with st.sidebar:
    st.title("技能智能分析设置")
    api_key = st.text_input("请输入 API Token:", type="password")
    temperature = st.slider("temperature", 0.0, 1.5, 0.7, step=0.1)
    if api_key:
        client = init_glm_ai(api_key)
        st.success("✅ API Key 已配置")
    else:
        client = None
        st.warning("⚠️ 未配置 API Key，将无法使用大模型自然语言解读")

# ✅ 使用更稳定的缓存机制（适合大数据）
@st.cache_resource(show_spinner=False)
def load_dataset():
    df = pd.read_csv("data/招聘数据集(含技能列表）.csv")
    df.dropna(subset=["skill_list", "positionName"], inplace=True)
    skill_data = df["skill_list"].apply(lambda x: x.split(",")).tolist()
    return df, skill_data

# ✅ 加载提示 + 视觉提醒
st.info("⚠️ 数据集较大，加载可能需要几秒钟，请耐心等待...")
with st.spinner("📂 正在加载数据，请稍等..."):
    dataset, skill_data = load_dataset()

# 🚀 页面主体
st.title("🔍 实验3：技术关联性挖掘与推荐")

option = st.radio("请选择查询类型", [
    "我会某个技能，适合什么岗位？",
    "某个岗位需要什么技能？",
    "我掌握某个技能，推荐我学习什么？"
])

# 🔍 模式一：技能 → 岗位
if option == "我会某个技能，适合什么岗位？":
    top_skills = pd.Series(sum(skill_data, [])).value_counts().head(100).index.tolist()
    skill = st.selectbox("请选择技能（前100高频）", top_skills)
    if st.button("查询关联岗位"):
        with st.spinner("🔍 正在分析岗位匹配..."):
            result = cacu_skill_position_wordcount(dataset, skill, prompt=f"我掌握{skill}可以从事哪些岗位？")
            st.markdown("📌 **推荐岗位：**")
            st.markdown(result["summary"])
            if client:
                reply = client.chat.completions.create(
                    model="glm-4",
                    messages=[{"role": "user", "content": result["prompt"]}],
                    temperature=temperature
                )
                st.markdown("🤖 **智能解读：**")
                st.markdown(reply.choices[0].message.content)

# 🔍 模式二：岗位 → 技能
elif option == "某个岗位需要什么技能？":
    job = st.selectbox("请选择岗位", dataset['positionName'].dropna().unique())
    if st.button("查询技能需求"):
        with st.spinner("📊 正在分析技能需求..."):
            result = cacu_postion_skill_wordcount(dataset, job, prompt=f"{job}岗位需要掌握哪些技能？")
            st.markdown("📌 **核心技能：**")
            st.markdown(result["summary"])
            if client:
                reply = client.chat.completions.create(
                    model="glm-4",
                    messages=[{"role": "user", "content": result["prompt"]}],
                    temperature=temperature
                )
                st.markdown("🤖 **智能解读：**")
                st.markdown(reply.choices[0].message.content)

# 📈 模式三：技能 → 推荐学习技能（Apriori）
elif option == "我掌握某个技能，推荐我学习什么？":
    top_skills = pd.Series(sum(skill_data, [])).value_counts().head(100).index.tolist()
    skill = st.selectbox("请选择技能（前100高频）", top_skills)
    if st.button("推荐学习技能"):
        with st.spinner("📈 正在推荐关联技能（Apriori）..."):
            result = get_asso_skill(dataset, skill, prompt=f"我掌握了{skill}，推荐我进一步学习哪些技能？")
            st.markdown("📌 **推荐技能：**")
            st.markdown(result["summary"])
            if client:
                reply = client.chat.completions.create(
                    model="glm-4",
                    messages=[{"role": "user", "content": result["prompt"]}],
                    temperature=temperature
                )
                st.markdown("🤖 **智能解读：**")
                st.markdown(reply.choices[0].message.content)

st.markdown("---")
st.caption("数据来源：拉勾网招聘岗位数据（2023）")
