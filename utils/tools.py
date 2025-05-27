# 技能关联推荐函数（用户擅长某项技能，推荐其它相关技能）
query_frequent_items_tool = {
    "type": "function",
    "function": {
        "name": "get_asso_skill",
        "description": "当用户说“我会XXX，请推荐相关技术”时，调用该函数。用于推荐与用户已有技能最相关的其他技能。例如：“我学了C++，还需要学什么？”",
        "parameters": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": "技能名称，如java，python，linux等"
                }
            },
            "required": ["skill"]
        }
    }
}

# 技能 → 岗位推荐函数（用户掌握某技能，推荐适合岗位）
skill_to_pos_tool = {
    "type": "function",
    "function": {
        "name": "cacu_skill_position_wordcount",
        "description": "当用户说“我会XXX，能干什么岗位”时，调用该函数。例如：“我精通Python，可以做什么？”",
        "parameters": {
            "type": "object",
            "properties": {
                "skill": {
                    "type": "string",
                    "description": "用户掌握的技能，如python、linux等"
                }
            },
            "required": ["skill"]
        }
    }
}

# 岗位 → 技能推荐函数（用户想从事某岗位，推荐要学什么）
pos_to_skill_tool = {
    "type": "function",
    "function": {
        "name": "cacu_postion_skill_wordcount",
        "description": "当用户说“我要从事XXX岗位，要学什么”时，调用该函数。例如：“嵌入式岗位要学哪些技术？”",
        "parameters": {
            "type": "object",
            "properties": {
                "postionName": {
                    "type": "string",
                    "description": "岗位关键词，如嵌入式、后端、算法工程师等"
                }
            },
            "required": ["postionName"]
        }
    }
}

# 注册给 LLM 使用的工具列表
tools = [query_frequent_items_tool, skill_to_pos_tool, pos_to_skill_tool]
