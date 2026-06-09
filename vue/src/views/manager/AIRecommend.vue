<template>
  <div class="ai-container">
    <div class="ai-layout">
      <!-- 左侧会话列表 -->
      <div class="ai-sidebar">
        <div class="sidebar-header">
          <h3><el-icon style="vertical-align: middle; margin-right: 4px;"><VideoCamera /></el-icon>AI 电影推荐</h3>
        </div>
        <div class="new-session-btn">
          <el-button type="primary" style="width: 100%" @click="createNewSession">
            <el-icon><Plus /></el-icon> 新建对话
          </el-button>
        </div>
        <div class="session-list">
          <div
            v-for="sid in sessions"
            :key="sid"
            class="session-item"
            :class="{ active: sid === currentSessionId }"
            @click="switchSession(sid)"
          >
            <el-icon style="margin-right: 6px;"><ChatDotSquare /></el-icon>
            <span class="session-time">{{ formatSessionTime(sid) }}</span>
            <el-icon class="delete-btn" @click.stop="deleteSession(sid)"><Delete /></el-icon>
          </div>
          <div v-if="sessions.length === 0" class="empty-sessions">
            暂无对话记录
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="ai-chat">
        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesRef">
          <div v-if="messages.length === 0" class="welcome-msg">
            <div class="welcome-icon"><el-icon size="60"><VideoCameraFilled /></el-icon></div>
            <h2>AI 电影推荐小助手</h2>
            <p class="welcome-desc">你好！我是你的专属电影推荐助手，点击"新建对话"开始吧！</p>
            <p class="welcome-desc">告诉我你喜欢的电影类型、心情或演员，我来为你推荐好电影~</p>
            <div class="suggestion-tags">
              <el-tag
                v-for="tag in suggestionTags"
                :key="tag"
                class="suggestion-tag"
                @click="sendQuickMessage(tag)"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
            :class="msg.role === 'user' ? 'user-msg' : 'ai-msg'"
          >
            <div class="msg-avatar">
              <el-avatar :size="36" v-if="msg.role === 'user'" icon="UserFilled" />
              <el-avatar :size="36" v-else style="background-color: #409eff;" icon="VideoCameraFilled" />
            </div>
            <div class="msg-content-wrapper">
              <div class="msg-label">{{ msg.role === 'user' ? '你' : '电影小助手' }}</div>
              <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
            </div>
          </div>
          <div v-if="loading" class="message ai-msg">
            <div class="msg-avatar">
              <el-avatar :size="36" style="background-color: #409eff;" icon="VideoCameraFilled" />
            </div>
            <div class="msg-content-wrapper">
              <div class="msg-label">电影小助手</div>
              <div class="msg-content">
                <span class="typing-dots">思考中<span>.</span><span>.</span><span>.</span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <el-input
            v-model="inputMessage"
            placeholder="输入你想看的电影类型、心情或明星..."
            size="large"
            clearable
            @keyup.enter="sendMessage"
            :disabled="loading || !currentSessionId"
          >
            <template #append>
              <el-button
                type="primary"
                @click="sendMessage"
                :disabled="!inputMessage.trim() || loading || !currentSessionId"
                style="height: 100%;"
              >
                <el-icon><Promotion /></el-icon> 发送
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const messagesRef = ref(null)
const messages = ref([])
const inputMessage = ref('')
const sessions = ref([])
const currentSessionId = ref(null)
const loading = ref(false)

const suggestionTags = [
  '推荐一部高分电影',
  '推荐喜剧片',
  '推荐科幻电影',
  '推荐评分9以上的电影',
  '推荐周星驰的电影',
  '推荐一部温暖治愈的电影',
]

function formatSessionTime(sid) {
  if (!sid) return ''
  const parts = sid.split('_')
  if (parts.length >= 2) {
    return parts[0] + ' ' + parts[1].substring(0, 5)
  }
  return sid
}

function renderMarkdown(text) {
  if (!text) return ''
  let html = text
  // 处理粗体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  // 处理换行
  html = html.replace(/\n/g, '<br>')
  return html
}

async function loadSessions() {
  try {
    const res = await request.get('/ai/sessions')
    if (res.code === '200') {
      sessions.value = res.data || []
    }
  } catch (e) {
    console.error('加载会话列表失败', e)
  }
}

async function createNewSession() {
  try {
    const res = await request.post('/ai/sessions')
    if (res.code === '200') {
      currentSessionId.value = res.data
      messages.value = []
      await loadSessions()
      ElMessage.success('新对话已创建！')
    } else {
      ElMessage.error(res.msg || '创建会话失败')
    }
  } catch (e) {
    ElMessage.error('创建会话失败')
  }
}

async function switchSession(sid) {
  if (sid === currentSessionId.value) return
  currentSessionId.value = sid
  try {
    const res = await request.get(`/ai/sessions/${sid}`)
    if (res.code === '200') {
      messages.value = res.data || []
      scrollToBottom()
    }
  } catch (e) {
    ElMessage.error('加载会话失败')
  }
}

async function deleteSession(sid) {
  try {
    await ElMessageBox.confirm('确定删除该对话记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const res = await request.delete(`/ai/sessions/${sid}`)
    if (res.code === '200') {
      if (currentSessionId.value === sid) {
        currentSessionId.value = null
        messages.value = []
      }
      await loadSessions()
      ElMessage.success('删除成功')
    }
  } catch (e) {
    // 取消删除不处理
  }
}

async function sendMessage() {
  const msg = inputMessage.value.trim()
  if (!msg || !currentSessionId.value) return

  inputMessage.value = ''
  messages.value.push({ role: 'user', content: msg })
  loading.value = true
  scrollToBottom()

  try {
    const res = await request.post('/ai/chat', {
      session_id: currentSessionId.value,
      message: msg,
    })
    if (res.code === '200') {
      messages.value.push({ role: 'assistant', content: res.data })
    } else {
      messages.value.push({ role: 'assistant', content: '抱歉，我遇到了一些问题，请稍后重试。' })
    }
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '网络异常，请检查连接后重试。' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function sendQuickMessage(tag) {
  inputMessage.value = tag
  sendMessage()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(async () => {
  await loadSessions()
  if (sessions.value.length > 0) {
    await switchSession(sessions.value[0])
  }
})
</script>

<style scoped>
.ai-container {
  height: calc(100vh - 80px);
  background: #f0f2f5;
  border-radius: 8px;
  overflow: hidden;
}

.ai-layout {
  display: flex;
  height: 100%;
}

/* 左侧栏 */
.ai-sidebar {
  width: 240px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px 16px 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.new-session-btn {
  padding: 12px 16px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 6px;
  margin-bottom: 2px;
  transition: all 0.2s;
}

.session-item:hover {
  background: #f5f7fa;
}

.session-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.session-time {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
  color: #c0c4cc;
  cursor: pointer;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #f56c6c;
}

.empty-sessions {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 13px;
}

/* 聊天区域 */
.ai-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-msg {
  text-align: center;
  padding: 60px 20px;
}

.welcome-icon {
  margin-bottom: 16px;
  color: #409eff;
}

.welcome-msg h2 {
  margin: 0 0 12px;
  color: #303133;
  font-size: 22px;
}

.welcome-desc {
  color: #606266;
  font-size: 14px;
  margin: 4px 0;
}

.suggestion-tags {
  margin-top: 24px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.suggestion-tag {
  cursor: pointer;
  font-size: 13px;
  padding: 4px 12px;
}

.suggestion-tag:hover {
  transform: scale(1.05);
}

/* 消息样式 */
.message {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.user-msg {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.msg-content-wrapper {
  max-width: 70%;
}

.msg-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.user-msg .msg-label {
  text-align: right;
}

.msg-content {
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

.user-msg .msg-content {
  background: #409eff;
  color: #fff;
}

.ai-msg .msg-content {
  background: #fff;
  border: 1px solid #eee;
}

/* 打字动画 */
.typing-dots span {
  animation: blink 1.4s infinite both;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}

/* 输入区域 */
.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
  background: #fff;
}
</style>