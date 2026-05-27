// pages/index/index.js
const app = getApp()

Page({
  data: {
    assistants: []
  },

  onLoad() {
    this.setData({
      assistants: app.globalData.assistants
    })
  },

  onShow() {
    // 每次显示页面时刷新助手列表
    this.setData({
      assistants: app.globalData.assistants
    })
  },

  // 开始对话
  startChat(e) {
    const assistant = e.currentTarget.dataset.assistant
    app.globalData.currentAssistant = assistant
    
    wx.navigateTo({
      url: '/pages/chat/chat'
    })
  },

  // 跳转到助手管理页面
  goToAssistants() {
    wx.switchTab({
      url: '/pages/assistants/assistants'
    })
  }
})
