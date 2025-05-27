import streamlit as st
st.set_page_config(page_title="实验1 - 招聘数据可视化", page_icon="📈")

import pandas as pd
from collections import Counter
from streamlit_echarts import st_echarts

# 加载数据
data = pd.read_csv('data/拉勾网2023招聘数据.csv')
data.columns = data.columns.str.strip()  # 清理列名中的空格

st.title("📊 实验1：招聘数据可视化")

# 选择要分析的问题
question = st.sidebar.selectbox(
    "请选择可视化问题",
    ["岗位招聘人数", "招聘岗位城市分布", "职位要求和岗位的关系"]
)

# 🧱 模块一：岗位招聘人数分布
if question == "岗位招聘人数":
    st.subheader("📌 各岗位招聘人数分布")
    selected_job = st.selectbox("选择职位", data['positionName'].dropna().unique())
    job_counts = data[data['positionName'] == selected_job]['positionName'].value_counts()
    st.bar_chart(job_counts)

# 🧱 模块二：城市中各岗位分布（饼图）
elif question == "招聘岗位城市分布":
    st.subheader("🏙️ 不同城市的岗位分布")
    selected_city = st.selectbox("选择城市", data['city'].dropna().unique())
    city_data = data[data['city'] == selected_city]
    job_counts_in_city = city_data['positionName'].value_counts()

    pie_options = {
        "title": {"text": f"{selected_city} 各岗位招聘占比", "left": "center"},
        "tooltip": {"trigger": "item"},
        "series": [{
            "name": "岗位分布",
            "type": "pie",
            "radius": "55%",
            "center": ["50%", "50%"],
            "data": [{"value": int(v), "name": k} for k, v in job_counts_in_city.items()],
            "label": {
                "show": True,
                "formatter": "{b}: {c} ({d}%)"
            }
        }]
    }
    st_echarts(options=pie_options)

# 🧱 模块三：岗位 -> 职位优势词频统计
elif question == "职位要求和岗位的关系":
    st.subheader("📌 职位要求关键词统计")
    selected_job = st.selectbox("选择职位", data['positionName'].dropna().unique())
    job_requirements = data[data['positionName'] == selected_job]['positionAdvantage'].dropna()

    all_requirements = ' '.join(job_requirements)
    requirements_list = all_requirements.split()
    most_common_requirements = Counter(requirements_list).most_common(5)

    if most_common_requirements:
        requirements, counts = zip(*most_common_requirements)
        st.bar_chart(pd.Series(counts, index=requirements))
    else:
        st.info("该岗位没有提取到明显的职位优势关键词。")
