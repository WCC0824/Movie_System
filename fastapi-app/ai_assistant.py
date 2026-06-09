"""
AI 电影推荐小助手
基于 DashScope (阿里云通义千问) API 实现智能电影推荐
"""
import json
import logging
import os
from datetime import datetime

from openai import OpenAI
from tortoise import Tortoise

from models import MovieInfo, Category
from settings import TORTOISE_ORM

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# AI 客户端配置
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 会话文件存储目录
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "ai_sessions")
if not os.path.exists(SESSIONS_DIR):
    os.mkdir(SESSIONS_DIR)

# 系统提示词（不包含动态电影数据部分）
SYSTEM_PROMPT_TEMPLATE = """# 角色定义
你是一个专业且热情的电影推荐小助手，名叫"电影小助手"，专门帮助用户发现想看的电影。
你掌握当前热门和经典的电影知识库，能够根据用户的口味、心情和需求，提供个性化的电影推荐。

## 核心能力
1. **智能推荐**：根据用户提到的心情、喜欢的类型、演员、导演等信息推荐电影
2. **电影问答**：回答关于电影剧情、演员、评分、上映时间等方面的问题
3. **知识科普**：分享电影相关的趣味知识、幕后故事、影评分析
4. **连续对话**：记住对话上下文，提供连贯的推荐体验

## 电影数据库（当前系统中的电影）
以下是本系统数据库中存储的所有电影信息，请基于这些电影进行推荐和问答：

{MOVIE_DATA}

## 回复规则
1. 推荐电影时，给出电影名称、评分、类型和简短推荐理由
2. 推荐时优先推荐系统中的电影，如果用户询问的电影不在系统中，可以基于你的知识回答
3. 回复简洁明了，推荐不超过5部电影
4. 语气热情友好，使用中文回复
5. 不回答与电影无关的问题
6. 初次对话时主动询问用户喜欢的电影类型或最近想看的类型

## 互动示例
- 用户说"推荐一部喜剧片" → 从数据库中筛选喜剧类型电影推荐
- 用户说"我喜欢周星驰的电影" → 推荐数据库中包含周星驰的电影
- 用户说"推荐一部评分高的电影" → 推荐数据库中评分较高的电影
- 用户说"有什么好看的科幻片" → 推荐数据库中科幻类型的电影
"""


def generate_session_id():
    """生成唯一会话 ID"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_session_file_path(session_id):
    """获取会话文件路径"""
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def load_session(session_id):
    """加载会话数据"""
    file_path = get_session_file_path(session_id)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_session(session_data):
    """保存会话数据"""
    file_path = get_session_file_path(session_data["session_id"])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


def list_sessions():
    """获取所有会话列表（按时间倒序）"""
    if not os.path.exists(SESSIONS_DIR):
        return []
    files = os.listdir(SESSIONS_DIR)
    session_ids = [f.split(".")[0] for f in files if f.endswith(".json")]
    session_ids.sort(reverse=True)
    return session_ids


def delete_session(session_id):
    """删除会话"""
    file_path = get_session_file_path(session_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


async def build_movie_data_string():
    """从数据库读取所有电影信息，构建成字符串供 AI 使用"""
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()

        movies = await MovieInfo.all().select_related("category")
        lines = []
        for movie in movies:
            category_name = movie.category.name if movie.category else "未分类"
            lines.append(
                f"- {movie.name} | 类型: {category_name} | 年份: {movie.year or '未知'} | "
                f"评分: {movie.rating or '未知'} | 导演: {movie.director or '未知'} | "
                f"演员: {movie.actors or '未知'} | 简介: {(movie.introduction or '无')[:100]}"
            )
        movie_data = "\n".join(lines) if lines else "暂无电影数据"
        logging.info(f"已加载 {len(lines)} 部电影数据用于 AI 推荐")

        await Tortoise.close_connections()
        return movie_data
    except Exception as e:
        logging.error(f"加载电影数据失败: {e}")
        return "暂无电影数据"


def get_system_prompt(movie_data):
    """获取完整的系统提示词"""
    return SYSTEM_PROMPT_TEMPLATE.replace("{MOVIE_DATA}", movie_data)


async def chat_with_ai(session_id, user_message):
    """
    与 AI 对话
    返回 AI 回复内容
    """
    # 1. 加载会话数据
    session_data = load_session(session_id)
    if not session_data:
        raise ValueError(f"会话不存在: {session_id}")

    # 2. 构建电影数据字符串
    movie_data = await build_movie_data_string()
    system_prompt = get_system_prompt(movie_data)

    # 3. 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]
    for msg in session_data["messages"]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    # 4. 调用 AI 大模型
    logging.info(f"[AI] 请求会话 {session_id}: {user_message[:50]}...")
    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=messages,
            stream=False,
            temperature=0.8,
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        logging.error(f"[AI] 调用失败: {e}")
        raise

    logging.info(f"[AI] 响应: {ai_response[:100]}...")

    # 5. 更新消息历史
    # 移除 system prompt
    messages.pop(0)
    messages.append({"role": "assistant", "content": ai_response})
    session_data["messages"] = messages
    save_session(session_data)

    return ai_response


def create_session():
    """创建新的会话"""
    session_id = generate_session_id()
    session_data = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }
    save_session(session_data)
    logging.info(f"[AI] 创建新会话: {session_id}")
    return session_id


def get_session_messages(session_id):
    """获取会话消息列表"""
    session_data = load_session(session_id)
    if not session_data:
        return None
    return session_data["messages"]