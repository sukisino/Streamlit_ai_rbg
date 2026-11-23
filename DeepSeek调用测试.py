from openai import OpenAI
import streamlit as st
from datetime import datetime
import json
from github import Github, GithubException

#实例化创建AI对象
client = OpenAI(api_key=st.secrets["API_KEY"], base_url="https://api.deepseek.com")


#创建世界的时间
if 'create_time' not in st.session_state:
    st.session_state.create_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

#创建会话记录
if 'messages' not in st.session_state:
    st.session_state.messages = []

#创建世界标签
if 'world_label' not in st.session_state:
    st.session_state.world_label = f"世界{st.session_state.create_time}"

#创建世界名称
if 'world_name' not in st.session_state:
    st.session_state.world_name = f'世界{st.session_state.create_time}'

#创建世界信息
if 'world_information' not in st.session_state:
    st.session_state.world_information = "你是一个异世界的rgb游戏系统，你的任务是根据用户给的大体世界观构建整个世界的世界观和框架，并且由你来设计游戏剧情（你给玩家剧情并让玩家做出行动，玩家的行为要有一定的限制，当玩家发送完回答后，你可以进行判断该行为是否合理,若不合理可以回复玩家哪里不符合，如果合理，你就按照玩家行为做出剧情的展开），还有就是游戏中的各种数值也是由你来设置"

#创建修改脏标记集合
if 'updata_dirty_mark' not in st.session_state:
    st.session_state.updata_dirty_mark = ()

#创建删除脏标记集合
if 'delete_dirty_mark' not in st.session_state:
    st.session_state.delete_dirty_mark = ()

#创建所有历史会话的仓库
if 'history_session_repo' not in st.session_state:
    st.session_state.history_session_repo = {}

#读取session_datas文件下的世界信息文件函数
def load_session_list():
    session_list = []
    if os.path.exists("session_datas"):
        file_list = os.listdir("session_datas")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-9])
    return session_list

#保存当前会话的信息函数
def save_session():
    if st.session_state.world_name:
        #构建会话对象存储数据
        session_data = {
            "world_label": st.session_state.world_label,
            "world_name": st.session_state.world_name,
            "world_information": st.session_state.world_information,
            "world_messages": st.session_state.messages,
        }

        #将构建的对象储存在history_world_repo
        history_world_repo[world_label] = session_data

        #将其标记上修改脏标签
        st.session_state.updata_dirty_mark.append(st.session_state.world_label)

#获取相应会话函数
def get_session(session):
    if os.path.exists(f"session_datas/{session}信息文件.json"):
        if st.session_state.messages:
            save_session()

        session_data = history_world_repo[session]
    return session_data

#加载相应会话函数
def load_session(session):
    session_data = get_session(session_state)
    st.session_state.world_label = session_data["world_label"]
    st.session_state.messages = session_data['world_messages']
    st.session_state.world_name = session_data["world_name"]
    st.session_state.world_information = session_data["world_information"]

#创建github仓库实例对象
@st.cache_resource
def get_github_repo():
    #从secrets读取token，创造Github实例
    github = Github(st.secrets["GITHUB_TOKEN"])
    repo = github.get_repo("sukisino/Streamlit_ai_rbg")
    return repo

#将系统文件保存到github仓库中
def save_session_to_github():
    repo = get_github_repo()

    #历遍所有在脏标记合集的会话，将其保存
    for world_label in st.session_state.updata_dirty_mark:
        path = f"session_datas/{world_label}.json"
        session_data = get_session(world_label)
        content = json.dumps(session_data, ensure_ascii=False, indent=2)

        try:
            existing = repo.get_contents(path)
            repo.update_file(path=path,message="更新会话{world_label}",content=content,sha=existing.sha,file_name=world_label)
        except GithubException:
            if GithubException.status == 404:
                return []
            raise  #-----------------------------------------------------------

#删除github仓库的系统文件
def delete_session_in_github():
    repo = get_github_repo()

    # 历遍所有在脏标记合集的会话，将其删除
    for world_label in st.session_state.delete_dirty_mark:
        path = f"session_datas/{world_label}.json"
        session_data = get_session(world_label)
        content = json.dumps(session_data, ensure_ascii=False, indent=2)

        try:
            existing = repo.get_contents(path)
            repo.delete_file(path=path, message="更新会话{world_label}", sha=existing.sha,
                             file_name=world_label)
        except GithubException:
            if GithubException.status == 404:
                return
            raise

#删除相应会话函数
def delete_session(session):
    #如果相应会话能找到，删除
    if session in st.session_state.history_session_repo.keys():
        st.session_state.history_session_repo.pop(session)

        #标记上删除脏标签
        st.session_state.delete_dirty_mark.append(session)

#侧边栏上部：当前世界信息面板
with st.sidebar:
    st.subheader("当前世界信息")
    world_name = st.text_input("当前世界名称", value=st.session_state.world_name)
    if world_name:
        st.session_state.world_name = world_name
    world_information = st.text_area("当前世界世界信息", value=st.session_state.world_information)
    if world_information:
        st.session_state.world_information = world_information
    if st.bottom("保存当前世界",width="stretch"):
        save_session()

#侧边栏下部：新世界和历史世界管理面板
with st.sidebar:
    st.subheader("世界控制面板")
    if st.button("创建新世界", width="stretch"):
        if st.session_state.messages:
            #保存当前会话信息
            save_session()

            #创建新的会话
            st.session_state.messages = []
            st.session_state.create_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            st.session_state.world_label = f'世界{st.session_state.create_time}'
            st.session_state.world_name = f'世界{st.session_state.create_time}'
            save_session()

    #历史世界管理面板
    st.text("历史世界记录")
    file_list = load_session_list()
    for history_world in file_list:
        #加载按钮和删除按钮
        col1,col2 = st.columns([4,1])
        with col1:
            if st.button(history_world, width="stretch", key=history_world, type="primary" if st.session_state.world_label == history_world else "secondary"):
                #如果当前会话内容不为空
                if st.session_state.messages:
                    #先保存当前会话再加载目标会话
                    save_session()
                    load_session(history_world)
                    st.rerun()
                else:
                    #否则直接加载目标会话
                    load_session(history_world)
                    st.rerun()
        with col2:
            if st.button('*', width="stretch", key=f"delete_{history_world}"):
                #判断删除的世界是否等于当前世界
                if st.session_state.world_label == history_world:
                    #是：删除的同时清除当前会话记录
                    delete_session(history_world)
                    print(f"{history_world}已删除")
                    st.session_state.messages = []
                    st.rerun()
                else:
                    #否：只删除当前会话
                    delete_session(history_world)

#显示初始化会话记录
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#聊天输入框
prompt = st.chat_input("")

#显示用户对话和记录用户对话
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_session()

    #调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": world_information},
            *st.session_state.messages,
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    ai_replys = st.empty()
    replys = ""

    for reply in response:
        if reply.choices[0].delta.content is not None:
            replys += reply.choices[0].delta.content
            ai_replys.chat_message("assistant").write(replys)

    #记录ai对话
    st.session_state.messages.append({"role": "assistant", "content": replys})
    save_session()
