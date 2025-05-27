import streamlit as st
st.set_page_config(page_title="实验2 - 函数调用", page_icon="🧠")

import streamlit as st
import pandas as pd
import plotly.express as px
from zhipuai import ZhipuAI

# 初始化Streamlit界面
st.title("招聘数据智能分析系统")

# 1. 加载数据（列名适配）
@st.cache_data
def load_data():
    df = pd.read_csv("data/拉勾网2023招聘数据.csv")
    # 数据预处理（修复薪资转换逻辑：同时替换大小写K）
    df['salary'] = df['salary'].str.replace(r'[kK]', '', regex=True).str.split('-').apply(  # 关键修改：正则匹配k/K
        lambda x: (float(x[0]) + float(x[-1]))/2 * 1000 if len(x) > 1 else float(x[0]) * 1000
    )
    # 技能列名修正：skills → skillLables
    df['skillLables'] = df['skillLables'].apply(lambda x: x.split(';') if isinstance(x, str) else [])  # 处理空值
    return df

df = load_data()

# 2. 初始化LLM客户端（无修改）
client = ZhipuAI(api_key="6f8b6e67674b4f7a87b5efacef35b666.KKUjmyxB9BjhN1L2")

# 3. 定义工具函数（参数描述适配新列名）
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_job_count",
            "description": "查询指定城市和职位名称的岗位数量",  # 描述修正
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "目标城市"},
                    "positionName": {"type": "string", "description": "目标职位名称"}  # 参数名修正
                },
                "required": ["city", "positionName"]  # 参数名修正
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_salary_range",
            "description": "查询指定职位名称的平均薪资范围",  # 描述修正
            "parameters": {
                "type": "object",
                "properties": {
                    "positionName": {"type": "string", "description": "目标职位名称"},  # 参数名修正
                    "workYear": {"type": "string", "description": "工作经验（如：3-5年）"}  # 参数名修正
                },
                "required": ["positionName"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_skill_demand",
            "description": "统计指定技能在岗位中的需求频率",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "description": "目标技能"}
                },
                "required": ["skill"]
            }
        }
    }
]

# 4. 定义本地函数（列名适配）
def query_job_count(city, positionName):  # 参数名修正
    # 职位列名修正：position → positionName
    filtered = df[(df['city'] == city) & (df['positionName'] == positionName)]
    return len(filtered)

def query_salary_range(positionName, workYear):  # 参数名修正
    # 职位列名修正：position → positionName；经验列名修正：experience → workYear
    filtered = df[
        (df['positionName'] == positionName) & 
        (df['workYear'] == workYear)
    ]
    if not filtered.empty:
        return f"{filtered['salary'].min()//1000}-{filtered['salary'].max()//1000}K"
    return "数据暂缺"

def query_skill_demand(skill):
    # 技能列名修正：skills → skillLables
    total = df[df['skillLables'].apply(lambda x: skill in x)].shape[0]
    return total

# 5. Streamlit交互界面（列名适配）
st.sidebar.title("查询功能")
function_choice = st.sidebar.radio("选择功能", ["岗位数量", "薪资查询", "技能需求"])

if function_choice == "岗位数量":
    # 职位列名修正：position → positionName
    city = st.selectbox("城市", df['city'].unique())
    positionName = st.selectbox("职位名称", df['positionName'].unique())  # 标签修正
    if st.button("查询"):
        # LLM调用时内容修正为新列名
        response = client.chat.completions.create(
            model="glm-4",
            messages=[{"role": "user", "content": f"用户查询{city}的{positionName}岗位数量"}],
            tools=tools,
            tool_choice="auto"
        )
        
        # 解析结果
        if response.choices[0].message.tool_calls:
            func_name = response.choices[0].message.tool_calls[0].function.name
            args = eval(response.choices[0].message.tool_calls[0].function.arguments)
            
            result = globals()[func_name](*args.values())
            st.write(f"岗位数量：​**​{result}个**​")
            
            # 结果转自然语言
            nl_response = client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "user", "content": f"用户问的是{city}的{positionName}岗位数量，查询结果是{result}。请用口语化中文解释这个结果。"}  # 关键修改：position → positionName
                ]
            )
            st.write(nl_response.choices[0].message.content)

elif function_choice == "薪资查询":
    # 职位列名修正：position → positionName；经验列名修正：experience → workYear
    positionName = st.selectbox("职位名称", df['positionName'].unique())  # 标签修正
    workYear = st.selectbox("工作经验", df['workYear'].unique())  # 选项来源修正
    if st.button("查询"):
        result = query_salary_range(positionName, workYear)
        st.write(f"平均薪资：**{result}**")

elif function_choice == "技能需求":
    # 技能列名修正：skills → skillLables
    skill = st.selectbox("技能名称", df['skillLables'].explode().unique())  # 来源列修正
    if st.button("查询"):
        result = query_skill_demand(skill)
        st.write(f"需求岗位数：**{result}个**")

# 6. 数据可视化（列名适配）
st.subheader("技能需求热力图")
# 技能列名修正：skills → skillLables
skill_counts = df['skillLables'].explode().value_counts().head(10)
fig = px.bar(skill_counts, title="Top 10热门技能需求")
st.plotly_chart(fig)

