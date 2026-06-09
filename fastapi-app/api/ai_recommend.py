"""
AI 电影推荐小助手 API 路由
"""
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from common.result import Result
from ai_assistant import (
    create_session,
    chat_with_ai,
    list_sessions,
    get_session_messages,
    delete_session,
)

router = APIRouter(prefix="/ai", tags=["AI推荐"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/sessions")
async def api_create_session():
    """创建新的对话会话"""
    try:
        session_id = create_session()
        return Result.success(session_id)
    except Exception as e:
        logging.error(f"创建会话失败: {e}")
        return Result.error(str(e))


@router.post("/chat")
async def api_chat(request: ChatRequest):
    """与 AI 对话"""
    try:
        ai_response = await chat_with_ai(request.session_id, request.message)
        return Result.success(ai_response)
    except ValueError as e:
        return Result.error(str(e))
    except Exception as e:
        logging.error(f"AI 对话失败: {e}")
        return Result.error(f"AI 服务异常，请稍后重试: {str(e)}")


@router.get("/sessions")
async def api_list_sessions():
    """获取会话列表"""
    try:
        sessions = list_sessions()
        return Result.success(sessions)
    except Exception as e:
        logging.error(f"获取会话列表失败: {e}")
        return Result.error(str(e))


@router.get("/sessions/{session_id}")
async def api_get_session(session_id: str):
    """获取指定会话的消息记录"""
    try:
        messages = get_session_messages(session_id)
        if messages is None:
            return Result.error("会话不存在")
        return Result.success(messages)
    except Exception as e:
        logging.error(f"获取会话消息失败: {e}")
        return Result.error(str(e))


@router.delete("/sessions/{session_id}")
async def api_delete_session(session_id: str):
    """删除会话"""
    try:
        if delete_session(session_id):
            return Result.success("删除成功")
        return Result.error("会话不存在")
    except Exception as e:
        logging.error(f"删除会话失败: {e}")
        return Result.error(str(e))