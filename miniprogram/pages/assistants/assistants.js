// pages/assistants/assistants.js
const app = getApp()

Page({
  data: {
    assistants: []
  },

  onLoad() {
    this.loadAssistants()
  },

  onShow() {
    this.loadAssistants()
  },

  // 加载助手列表
  loadAssistants() {
    const assistants = app.globalData.assistants.map(assistant => {
      const history = app.globalData.chatHistory[assistant.id] || []
      return {
        ...assistant,
        chatCount: history.length
      }
    })
    
    this.setData({ assistants })
  },

  // 选择助手开始对话
  selectAssistant(e) {
    const assistant = e.currentTarget.dataset.assistant
    app.globalData.currentAssistant = assistant
    
    wx.switchTab({
      url: '/pages/index/index'
    })
    
    setTimeout(() => {
      wx.navigateTo({
        url: '/pages/chat/chat'
      })
    }, 100)
  },

  // 添加新助手
  addAssistant() {
    wx.showToast({
      title: '添加功能开发中',
      icon: 'none'
    })
  }
})
