/**
 * Slide 09: 技术融合应用 - 三个助手平台
 * 展示上海"三个助手"数字化教学平台的应用
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("技术融合应用", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("三个助手平台：数字化教学转型", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 三个助手平台卡片布局
  const assistants = [
    {
      title: "教学助手",
      icon: "📚",
      color: theme.primary,
      features: [
        "AI备课资源智能推荐",
        "AR/VR沉浸式情境创设", 
        "语音识别与实时反馈",
        "个性化学习路径规划",
        "跨学科融合教学设计"
      ],
      x: 0.5,
      width: 2.9
    },
    {
      title: "评价检测助手", 
      icon: "📊",
      color: theme.secondary,
      features: [
        "过程性数据自动采集",
        "AI语音测评与纠音",
        "学习行为数据分析",
        "成长档案自动生成",
        "多维度能力评估报告"
      ],
      x: 3.5,
      width: 2.9
    },
    {
      title: "作业助手",
      icon: "✏️",
      color: theme.accent,
      features: [
        "智能作业布置与批改",
        "分层作业个性化推送",
        "云端协作与展示平台",
        "错题本与知识点巩固",
        "家校协同沟通桥梁"
      ],
      x: 6.5,
      width: 2.9
    }
  ];
  
  // 绘制三个助手卡片
  assistants.forEach((assistant, index) => {
    const yStart = 2.0;
    const cardHeight = 4.0;
    
    // 卡片背景
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: assistant.x, y: yStart, w: assistant.width, h: cardHeight,
      fill: { color: assistant.color + "10" },
      line: { color: assistant.color, width: 3 }
    });
    
    // 图标区域
    slide.addShape(pres.ShapeType.ELLIPSE, {
      x: assistant.x + assistant.width/2 - 0.6, y: yStart + 0.3, w: 1.2, h: 1.2,
      fill: { color: assistant.color },
      line: { color: "ffffff", width: 2 }
    });
    
    slide.addText(assistant.icon, {
      x: assistant.x + assistant.width/2 - 0.3, y: yStart + 0.6, w: 0.6, h: 0.6,
      fontSize: 28,
      align: 'center'
    });
    
    // 标题
    slide.addText(assistant.title, {
      x: assistant.x, y: yStart + 1.6, w: assistant.width, h: 0.6,
      fontSize: 20,
      bold: true,
      color: assistant.color,
      align: 'center'
    });
    
    // 功能列表
    assistant.features.forEach((feature, i) => {
      slide.addText(`• ${feature}`, {
        x: assistant.x + 0.2, y: yStart + 2.3 + i * 0.35, w: assistant.width - 0.4, h: 0.3,
        fontSize: 9,
        color: "333333",
        lineSpacing: 4
      });
    });
  });
  
  // 平台集成示意图
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.2, w: 9.0, h: 1.0,
    fill: { color: "f8f9fa" },
    line: { color: theme.light, width: 2 }
  });
  
  slide.addText("平台集成与数据流", {
    x: 0.6, y: 6.3, w: 8.8, h: 0.3,
    fontSize: 16,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 数据流图示
  const flowStages = ["教学助手\n收集学情", "评价助手\n分析数据", "作业助手\n精准干预", "学生成长\n可视化"];
  const flowColors = [theme.primary, theme.secondary, theme.accent, theme.light];
  
  for (let i = 0; i < flowStages.length; i++) {
    const xPos = 1.0 + i * 2.0;
    
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: xPos, y: 6.7, w: 1.8, h: 0.4,
      fill: { color: flowColors[i] },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(flowStages[i], {
      x: xPos, y: 6.7, w: 1.8, h: 0.4,
      fontSize: 9,
      bold: true,
      color: "ffffff",
      align: 'center'
    });
    
    // 连接箭头
    if (i < flowStages.length - 1) {
      slide.addShape(pres.ShapeType.TRIANGLE, {
        x: xPos + 1.9, y: 6.8, w: 0.2, h: 0.2,
        fill: { color: "666666" },
        rotate: 0
      });
      
      slide.addShape(pres.ShapeType.LINE, {
        x: xPos + 1.85, y: 6.9, w: 0.3, h: 0,
        line: { color: "666666", width: 1 }
      });
    }
  }
  
  // 页脚
  slide.addText("上海教育数字化转型 | 基于腾讯云、AI大模型、5G边缘计算技术", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };