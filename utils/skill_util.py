from .apriori import load_apriori, getAsso

# 推荐与某技能相关的其他技能（使用 apriori.bin）
def get_asso_skill(dataset, skill, prompt):
    print(f"get_asso_skill: {skill}")
    biga_load = load_apriori("apriori.bin")
    s = getAsso(biga_load, skill.lower(), 0.1)
    print(f"{skill} 对应的关联技术是：{s}")

    if len(s) == 0:
        return {
            "summary": f"{skill} 没有查到关联技能",
            "prompt": f"暂时查不到 {skill} 的关联技能，请解释可能原因。"
        }

    joined = ', '.join(list(s))
    return {
        "summary": joined,
        "prompt": f"针对问题 {skill}，我查询到关联性最高的技能是：{joined}，请将查询结果组织成自然语言说明，可以附加一些学习建议，总字数不超过200字。"
    }

# 技能 → 岗位推荐
def cacu_skill_position_wordcount(dataset, skill, prompt):
    skill = skill.lower()
    postion_dict = {}
    for i in range(len(dataset)):
        skills = dataset.iloc[i]['skill_list'].split(',')
        if skill in [s.lower() for s in skills]:
            name = dataset.iloc[i]['positionName']
            postion_dict[name] = postion_dict.get(name, 0) + 1

    sorted_postions = sorted(postion_dict.items(), key=lambda x: x[1], reverse=True)
    top_jobs = [p[0] for p in sorted_postions[:5]]

    return {
        "summary": ', '.join(top_jobs),
        "prompt": f"针对问题：掌握{skill}可以从事什么岗位？该技能关联最多的岗位包括：{', '.join(top_jobs)}，请用自然语言对其进行解读。"
    }

# 岗位 → 技能推荐
def cacu_postion_skill_wordcount(dataset, postionName, prompt):
    def compare_str(a, b):
        a, b = a.lower(), b.lower()
        return b in a

    postion_data = dataset[dataset['positionName'].apply(lambda x: compare_str(str(x), postionName))]
    skill_list = postion_data['skill_list'].dropna().tolist()

    word_dict = {}
    for row in skill_list:
        for word in row.split(','):
            word_dict[word] = word_dict.get(word, 0) + 1

    sorted_words = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    top_words = [w[0] for w in sorted_words[:10]]

    return {
        "summary": ', '.join(top_words),
        "prompt": f"针对问题：{postionName}岗位需要什么技能？该岗位最常见的技能包括：{', '.join(top_words)}，请用自然语言进行说明。"
    }
