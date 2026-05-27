// utils/ai-service.js
// AI服务封装,支持多种AI提供商

class AIService {
  constructor(config) {
    this.config = {
      provider: config.provider || 'zhipu', // zhipu, openai, baidu, etc.
      apiKey: config.apiKey || '',
      baseURL: config.baseURL || '',
      model: config.model || 'glm-4'
    }
  }

  // 设置配置
  setConfig(config) {
    this.config = { ...this.config, ...config }
  }

  // 发送聊天请求
  async chat(messages, systemPrompt) {
    const requestMessages = [
      { role: 'system', content: systemPrompt },
      ...messages
    ]

    try {
      let response
      
      switch (this.config.provider) {
        case 'zhipu':
          response = await this.callZhipuAI(requestMessages)
          break
        case 'openai':
          response = await this.callOpenAI(requestMessages)
          break
        case 'baidu':
          response = await this.callBaiduAI(requestMessages)
          break
        default:
          throw new Error('不支持的AI提供商')
      }

      return response
    } catch (error) {
      console.error('AI调用失败:', error)
      throw error
    }
  }

  // 智谱AI调用
  async callZhipuAI(messages) {
    const url = this.config.baseURL || 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        data: {
          model: this.config.model || 'glm-4',
          messages: messages,
          temperature: 0.7,
          max_tokens: 2000,
          stream: false
        },
        success: (res) => {
          if (res.statusCode === 200 && res.data.choices && res.data.choices[0]) {
            resolve(res.data.choices[0].message.content)
          } else {
            reject(new Error(res.data.error?.message || '请求失败'))
          }
        },
        fail: (err) => {
          reject(new Error('网络请求失败'))
        }
      })
    })
  }

  // OpenAI调用
  async callOpenAI(messages) {
    const url = this.config.baseURL || 'https://api.openai.com/v1/chat/completions'
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        data: {
          model: this.config.model || 'gpt-3.5-turbo',
          messages: messages,
          temperature: 0.7,
          max_tokens: 2000
        },
        success: (res) => {
          if (res.statusCode === 200 && res.data.choices && res.data.choices[0]) {
            resolve(res.data.choices[0].message.content)
          } else {
            reject(new Error(res.data.error?.message || '请求失败'))
          }
        },
        fail: (err) => {
          reject(new Error('网络请求失败'))
        }
      })
    })
  }

  // 百度文心一言调用
  async callBaiduAI(messages) {
    // 百度文心一言需要先获取access_token
    // 这里简化处理,实际使用时需要实现token获取逻辑
    const url = this.config.baseURL
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: url,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          messages: messages
        },
        success: (res) => {
          if (res.statusCode === 200 && res.data.result) {
            resolve(res.data.result)
          } else {
            reject(new Error(res.data.error_msg || '请求失败'))
          }
        },
        fail: (err) => {
          reject(new Error('网络请求失败'))
        }
      })
    })
  }

  // 流式聊天(支持打字机效果)
  async streamChat(messages, systemPrompt, onChunk) {
    // 微信小程序暂不支持标准的SSE流式响应
    // 这里可以模拟打字机效果
    const fullResponse = await this.chat(messages, systemPrompt)
    
    // 模拟流式输出
    const chunks = fullResponse.split('')
    let currentText = ''
    
    for (const chunk of chunks) {
      currentText += chunk
      onChunk(currentText)
      await this.delay(30) // 30ms延迟模拟打字效果
    }
    
    return fullResponse
  }

  // 延迟函数
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// 导出单例
const aiService = new AIService({
  provider: 'zhipu',
  apiKey: '',
  model: 'glm-4'
})

module.exports = {
  AIService,
  aiService
}
