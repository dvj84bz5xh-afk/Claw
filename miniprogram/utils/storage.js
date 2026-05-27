// utils/storage.js
// 本地存储管理工具

const StorageKeys = {
  CHAT_HISTORY: 'chat_history',
  USER_INFO: 'user_info',
  ASSISTANTS: 'assistants',
  SETTINGS: 'settings',
  API_CONFIG: 'api_config'
}

class StorageManager {
  // 保存数据
  static set(key, data) {
    try {
      wx.setStorageSync(key, data)
      return true
    } catch (e) {
      console.error('保存数据失败:', e)
      return false
    }
  }

  // 获取数据
  static get(key, defaultValue = null) {
    try {
      const data = wx.getStorageSync(key)
      return data !== undefined ? data : defaultValue
    } catch (e) {
      console.error('获取数据失败:', e)
      return defaultValue
    }
  }

  // 删除数据
  static remove(key) {
    try {
      wx.removeStorageSync(key)
      return true
    } catch (e) {
      console.error('删除数据失败:', e)
      return false
    }
  }

  // 清空所有数据
  static clear() {
    try {
      wx.clearStorageSync()
      return true
    } catch (e) {
      console.error('清空数据失败:', e)
      return false
    }
  }

  // ==================== 聊天记录相关 ====================
  
  // 保存聊天记录
  static saveChatHistory(assistantId, messages) {
    const allHistory = this.get(StorageKeys.CHAT_HISTORY, {})
    allHistory[assistantId] = messages
    return this.set(StorageKeys.CHAT_HISTORY, allHistory)
  }

  // 获取聊天记录
  static getChatHistory(assistantId) {
    const allHistory = this.get(StorageKeys.CHAT_HISTORY, {})
    return allHistory[assistantId] || []
  }

  // 删除聊天记录
  static deleteChatHistory(assistantId) {
    const allHistory = this.get(StorageKeys.CHAT_HISTORY, {})
    delete allHistory[assistantId]
    return this.set(StorageKeys.CHAT_HISTORY, allHistory)
  }

  // 清空所有聊天记录
  static clearAllChatHistory() {
    return this.remove(StorageKeys.CHAT_HISTORY)
  }

  // ==================== 用户设置相关 ====================
  
  // 保存API配置
  static saveApiConfig(config) {
    return this.set(StorageKeys.API_CONFIG, config)
  }

  // 获取API配置
  static getApiConfig() {
    return this.get(StorageKeys.API_CONFIG, {
      provider: 'zhipu',
      apiKey: '',
      model: 'glm-4'
    })
  }

  // 保存设置
  static saveSettings(settings) {
    return this.set(StorageKeys.SETTINGS, settings)
  }

  // 获取设置
  static getSettings() {
    return this.get(StorageKeys.SETTINGS, {
      theme: 'light',
      fontSize: 'normal',
      autoPlayVoice: false
    })
  }
}

module.exports = {
  StorageKeys,
  StorageManager
}
