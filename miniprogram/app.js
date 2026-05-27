// app.js
App({
  globalData: {
    // AI助手配置列表
    assistants: [
      {
        id: 'medical',
        name: '医疗咨询专家',
        avatar: '/images/medical.png',
        description: '提供医疗健康咨询和建议',
        systemPrompt: '你是一位专业的医疗咨询专家,具有丰富的医学知识。请为用户提供准确、专业的医疗建议,但也要提醒用户在严重情况下及时就医。'
      },
      {
        id: 'legal',
        name: '法律顾问',
        avatar: '/images/legal.png',
        description: '提供法律咨询和解答',
        systemPrompt: '你是一位专业的法律顾问,熟悉各类法律法规。请为用户提供法律咨询,但要明确说明不能替代专业律师的正式法律服务。'
      },
      {
        id: 'tech',
        name: '技术专家',
        avatar: '/images/tech.png',
        description: '编程和技术问题解答',
        systemPrompt: '你是一位资深的技术专家,精通多种编程语言和技术栈。请为用户提供专业、准确的技术解答和代码示例。'
      },
      {
        id: 'education',
        name: '教育顾问',
        avatar: '/images/education.png',
        description: '教育和学习指导',
        systemPrompt: '你是一位经验丰富的教育顾问,擅长学习和教学指导。请为用户提供有效的学习方法建议和教育咨询。'
      },
      {
        id: 'life',
        name: '生活顾问',
        avatar: '/images/life.png',
        description: '生活建议和指导',
        systemPrompt: '你是一位贴心的生活顾问,关注用户的日常生活需求。请为用户提供实用的生活建议和温馨关怀。'
      },
      {
        id: 'finance',
        name: '理财顾问',
        avatar: '/images/finance.png',
        description: '投资理财建议',
        systemPrompt: '你是一位专业的理财顾问,具有丰富的金融投资知识。请为用户提供理财建议,但要提醒投资有风险,需谨慎决策。'
      }
    ],
    currentAssistant: null,
    chatHistory: {},
    // AI API配置(需要用户替换为实际的API配置)
    aiConfig: {
      baseURL: 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
      apiKey: '', // 用户需要填写自己的API密钥
      model: 'glm-4'
    }
  },

  onLaunch() {
    // 初始化当前助手
    if (!this.globalData.currentAssistant) {
      this.globalData.currentAssistant = this.globalData.assistants[0];
    }
    
    // 从本地存储加载聊天记录
    this.loadChatHistory();
  },

  // 保存聊天记录到本地
  saveChatHistory(assistantId, messages) {
    const chatHistory = this.globalData.chatHistory;
    chatHistory[assistantId] = messages;
    wx.setStorageSync('chatHistory', chatHistory);
  },

  // 从本地加载聊天记录
  loadChatHistory() {
    try {
      const chatHistory = wx.getStorageSync('chatHistory');
      if (chatHistory) {
        this.globalData.chatHistory = chatHistory;
      }
    } catch (e) {
      console.error('加载聊天记录失败:', e);
    }
  },

  // 清除指定助手的聊天记录
  clearChatHistory(assistantId) {
    if (this.globalData.chatHistory[assistantId]) {
      delete this.globalData.chatHistory[assistantId];
      wx.setStorageSync('chatHistory', this.globalData.chatHistory);
    }
  },

  // 调用AI API
  async callAI(messages, systemPrompt) {
    const config = this.globalData.aiConfig;
    
    if (!config.apiKey) {
      throw new Error('请先在代码中配置AI API密钥');
    }

    // 构建消息数组
    const requestMessages = [
      { role: 'system', content: systemPrompt },
      ...messages
    ];

    try {
      const response = await wx.request({
        url: config.baseURL,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.apiKey}`
        },
        data: {
          model: config.model,
          messages: requestMessages,
          temperature: 0.7,
          max_tokens: 2000
        }
      });

      if (response.statusCode === 200 && response.data.choices && response.data.choices[0]) {
        return response.data.choices[0].message.content;
      } else {
        throw new Error('AI请求失败');
      }
    } catch (error) {
      console.error('调用AI失败:', error);
      throw error;
    }
  }
});
