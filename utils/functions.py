import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
import time

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def save_fig(fig):
    os.makedirs("figures", exist_ok=True)
    path = f"figures/{int(time.time())}.png"
    fig.savefig(path)
    return path

def get_skill_distribution(dataset, skill=None, chart_type="饼图", **kwargs):
    if not skill:
        return {"text": "未指定技能关键词。", "plot": None, "table": None}

    df = dataset.copy()
    df = df[df["skill_list"].str.contains(skill, case=False, na=False)]
    if df.empty:
        return {"text": f"技能 “{skill}” 在数据中没有找到对应岗位。", "plot": None, "table": None}

    if chart_type == "表格":
        rdata = df[["positionName", "companyFullName", "city", "salary", "workYear", "education"]].head(10)
        return {
            "text": f"技能 “{skill}” 相关的招聘岗位如下（最多展示 10 条）：",
            "plot": None,
            "table": rdata
        }

    top_jobs = df["positionName"].value_counts().head(10)
    fig, ax = plt.subplots()
    if chart_type == "条形图":
        top_jobs.plot(kind="barh", ax=ax)
        ax.set_xlabel("岗位数量")
    else:
        top_jobs.plot(kind="pie", autopct='%1.1f%%', startangle=90, ax=ax)
        ax.set_ylabel("")
    ax.set_title(f"{skill} 技能对应热门岗位分布")
    img_path = save_fig(fig)

    return {
        "text": f"技能 “{skill}” 对应的热门岗位有：{', '.join(top_jobs.index)}。",
        "plot": img_path,
        "table": None
    }

def get_recommend_jobs(dataset, keyword=None, **kwargs):
    if not keyword:
        return {"text": "请提供岗位关键词（如 Java、C++ 等）", "plot": None, "table": None}

    df = dataset.copy()
    df = df[df["positionName"].str.contains(keyword, case=False, na=False)]
    if df.empty:
        return {"text": f"未找到包含“{keyword}”的相关岗位信息。", "plot": None, "table": None}

    rdata = df[["positionName", "companyFullName", "city", "salary", "workYear", "education"]].head(10)
    return {
        "text": f"以下是与“{keyword}”相关的招聘岗位推荐（最多展示 10 条）：",
        "plot": None,
        "table": rdata
    }

def get_skill_requirements(dataset, keyword=None, **kwargs):
    if not keyword:
        return {"text": "请提供岗位关键词（如 嵌入式）", "plot": None, "table": None}

    df = dataset.copy()
    df = df[df["positionName"].str.contains(keyword, case=False, na=False)]
    if df.empty:
        return {"text": f"未找到包含“{keyword}”的岗位，无法分析技能要求。", "plot": None, "table": None}

    skill_series = df["skill_list"].dropna().str.split(",")
    all_skills = [s.strip() for sublist in skill_series for s in sublist]
    skill_counts = pd.Series(all_skills).value_counts().head(15)

    fig, ax = plt.subplots()
    skill_counts.plot(kind="bar", ax=ax)
    ax.set_title(f"{keyword} 岗位对应常见技能分布")
    ax.set_ylabel("需求频次")
    ax.set_xlabel("技能")
    img_path = save_fig(fig)

    return {
        "text": f"{keyword} 岗位要求具备如下核心技能（Top 15）：",
        "plot": img_path,
        "table": None
    }

def get_skill_requirements(dataset, keyword=None, **kwargs):
    if not keyword:
        return {"text": "请提供岗位关键词（如 嵌入式）", "plot": None, "table": None}

    df = dataset.copy()
    df = df[df["positionName"].str.contains(keyword, case=False, na=False)]

    if df.empty:
        return {"text": f"未找到包含“{keyword}”的岗位，无法分析技能要求。", "plot": None, "table": None}

    skill_series = df["skill_list"].dropna().str.split(",")
    all_skills = [s.strip() for sublist in skill_series for s in sublist]
    skill_counts = pd.Series(all_skills).value_counts().head(15)

    fig, ax = plt.subplots()
    skill_counts.plot(kind="bar", ax=ax)
    ax.set_title(f"{keyword} 岗位对应常见技能分布")
    ax.set_ylabel("需求频次")
    ax.set_xlabel("技能")
    img_path = save_fig(fig)

    # 🔍 分析文字（可根据 top3 技能定制）
    top_skills = skill_counts.head(3).index.tolist()
    desc = (
        f"{keyword} 岗位通常要求掌握如 {top_skills[0]}、{top_skills[1]} 和 {top_skills[2]} 等核心技能，"
        "这些技能在硬件开发、驱动编程、系统通信等场景中被广泛应用。"
        "建议重点学习相关技术，同时结合项目实践进一步加深理解与运用。"
    )

    return {
        "text": f"{keyword} 岗位要求具备如下核心技能（Top 15）：\n\n{desc}",
        "plot": img_path,
        "table": None
    }
