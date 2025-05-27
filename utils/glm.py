from zhipuai import ZhipuAI
import json
import streamlit as st  # ✅ 添加用于读取 session_state（如 chart_type）

def init_glm_ai(api_key):
    return ZhipuAI(api_key=api_key)

def chatTools(client, prompt, tools, temperature=0.6):
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            },
        ],
        tools=tools,
        tool_choice="auto",
        temperature=temperature
    )
    return response.choices[0]

def chat_glmOnce(client, prompt):
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

def ask_glm(client, tools, temperature, content, function_list, dataset, chart_type=None):
    ack = chatTools(client, content, tools, temperature)

    if ack.finish_reason == "tool_calls":
        tool_call = ack.message.tool_calls[0]
        function_name = tool_call.function.name
        function_args_str = tool_call.function.arguments

        try:
            function_args_dict = json.loads(function_args_str)
        except json.JSONDecodeError:
            return {"text": "函数参数解析失败（JSON 格式不正确）", "plot": None}

        if function_name not in function_list:
            return {"text": f"未找到函数：{function_name}", "plot": None}

        # ✅ 注入上下文信息，包括 chart_type
        function_args_dict["dataset"] = dataset
        function_args_dict["prompt"] = content
        function_args_dict["chart_type"] = chart_type or st.session_state.get("chart_type", "饼图")

        # ✅ 执行函数
        func = function_list[function_name]
        return func(**function_args_dict)

    return {
        "text": ack.message.content,
        "plot": None,
        "table": None
    }
