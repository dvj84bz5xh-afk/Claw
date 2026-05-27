// pages/chat/chat.js
const app = getApp()

Page({
  data: {
    currentAssistant: null,
    messages: [],
    inputText: '',
    loading: false,
    scrollToView: '',
    welcomeMessage: '您好!我是' + app.globalData.assistants[0].name + ',很高兴为您服务。请问有什么可以帮助您的吗?'
  },

  onLoad(options) {
    // 设置当前助手
    const currentAssistant = app.globalData.currentAssistant
    this.setData({
      currentAssistant,
      welcomeMessage: `您好!我是${currentAssistant.name},很高兴为您服务。请问有什么可以帮助您的吗?`
    })

    // 加载历史聊天记录
    this.loadChatHistory()
  },

  onShow() {
    // 更新助手信息
    const currentAssistant = app.globalData.currentAssistant
    if (currentAssistant) {
      this.setData({
        currentAssistant
      })
    }
  },

  // 加载聊天历史
  loadChatHistory() {
    const history = app.globalData.chatHistory[this.data.currentAssistant.id] || []
    const messages = history.map(msg => ({
      ...msg,
      time: this.formatTime(msg.timestamp)
    }))
    
    this.setData({ messages })
    
    // 滚动到底部
    if (messages.length > 0) {
      this.scrollToBottom()
    }
  },

  // 输入变化
  onInput(e) {
    this.setData({
      inputText: e.detail.value
    })
  },

  // 发送消息
  async sendMessage() {
    const inputText = this.data.inputText.trim()
    
    if (!inputText) {
      return
    }

    if (this.data.loading) {
      wx.showToast({
        title: '请等待回复',
        icon: 'none'
      })
      return
    }

    // 添加用户消息
    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: Date.now(),
      time: this.formatTime(Date.now())
    }

    const newMessages = [...this.data.messages, userMessage]
    
    this.setData({
      messages: newMessages,
      inputText: '',
      loading: true
    })

    this.scrollToBottom()

    try {
      // 调用AI API
      const messagesForAPI = this.data.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const assistantReply = await app.callAI(
        messagesForAPI,
        this.data.currentAssistant.systemPrompt
      )

      // 添加AI回复
      const assistantMessage = {
        role: 'assistant',
        content: assistantReply,
        timestamp: Date.now(),
        time: this.formatTime(Date.now())
      }

      const updatedMessages = [...newMessages, assistantMessage]
      
      this.setData({
        messages: updatedMessages,
        loading: false
      })

      // 保存到本地
      app.saveChatHistory(this.data.currentAssistant.id, updatedMessages)
      
      this.scrollToBottom()

    } catch (error) {
      console.error('发送消息失败:', error)
      
      this.setData({
        loading: false
      })

      wx.showModal({
        title: '提示',
        content: error.message || '发送失败,请稍后重试',
        showCancel: false
      })

      // 移除用户消息
      const messages = this.data.messages.filter(msg => msg !== userMessage)
      this.setData({ messages })
    }
  },

  // 清除聊天记录
  clearHistory() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除与该助手的所有对话记录吗?',
      success: (res) => {
        if (res.confirm) {
          app.clearChatHistory(this.data.currentAssistant.id)
          this.setData({
            messages: [],
            scrollToView: 'welcome'
          })
          
          wx.showToast({
            title: '已清除',
            icon: 'success'
          })
        }
      }
    })
  },

  // 滚动到底部
  scrollToBottom() {
    const lastIndex = this.data.messages.length - 1
    if (lastIndex >= 0) {
      this.setData({
        scrollToView: `msg-${lastIndex}`
      })
    }
  },

  // 格式化时间
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    
    // 如果是今天,只显示时间
    if (date.toDateString() === now.toDateString()) {
      return `${hours}:${minutes}`
    }
    
    // 否则显示日期和时间
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${month}/${day} ${hours}:${minutes}`
  }
})
