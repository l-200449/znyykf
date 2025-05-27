import streamlit as st
from utils.auth import authenticate_user, register_user

# 页面基本配置
st.set_page_config(page_title="招聘智能推荐系统", page_icon="🤖", layout="wide")

# 登录状态初始化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 未登录时显示登录/注册界面
if not st.session_state.logged_in:
    st.title("🔐 欢迎使用招聘智能推荐系统")

    tab1, tab2 = st.tabs(["已有账户登录", "注册新账户"])

    with tab1:
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("登录"):
            if authenticate_user(username, password):
                st.success("✅ 登录成功，欢迎回来！")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ 用户名或密码错误，请重试。")

    with tab2:
        new_user = st.text_input("新用户名", key="new_user")
        new_pass = st.text_input("设置密码", type="password", key="new_pass")
        if st.button("注册"):
            if register_user(new_user, new_pass):
                st.success("✅ 注册成功！请返回登录页登录")
            else:
                st.warning("⚠️ 用户名已存在，请更换")

    st.stop()  # 阻止后续页面渲染

# 登录成功后显示主界面
st.title(f"🎉 欢迎，{st.session_state.username}！")

st.sidebar.title("📚 功能导航")
st.sidebar.page_link("pages/1_实验1_招聘数据可视化.py", label="实验1：数据可视化", icon="📊")
st.sidebar.page_link("pages/2_实验2_LLM函数调用.py", label="实验2：LLM函数调用", icon="🤖")
st.sidebar.page_link("pages/3_实验3_技术关联性挖掘.py", label="实验3：技能关联推荐", icon="🔍")
st.sidebar.page_link("pages/4_实验4_招聘智能问答助手.py", label="实验4：AI问答助手", icon="💬")

# 登出功能
if st.sidebar.button("退出登录"):
    st.session_state.logged_in = False
    st.experimental_rerun()

st.markdown("---")
st.info("请通过左侧导航栏进入各子模块功能页面。")
