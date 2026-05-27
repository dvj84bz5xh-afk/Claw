/**
 * Slide 10: 教学成效与反思 - 基于数据的效果分析
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("教学成效与反思", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("基于数据的效果分析与教学改进", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 左侧：数据驱动的成效分析
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.8, w: 4.5, h: 4.5,
    fill: { color: "f8f9fa" },
    line: { color: theme.primary, width: 2 }
  });
  
  slide.addText("数据驱动的成效分析", {
    x: 0.6, y: 1.9, w: 4.3, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 四维度成效指标
  const metrics = [
    {
      title: "语言能力提升",
      data: "92%",
      description: "核心词汇掌握率",
      color: theme.primary,
      icon: "💬"
    },
    {
      title: "学习兴趣激发", 
      data: "88%",
      description: "课堂参与度提高",
      color: theme.secondary,
      icon: "🌟"
    },
    {
      title: "技术素养培养",
      data: "85%",
      description: "数字工具使用熟练度",
      color: theme.accent,
      icon: "💻"
    },
    {
      title: "五育融合成效",
      data: "90%",
      description: "综合素养发展评价",
      color: theme.light,
      icon: "🎯"
    }
  ];
  
  metrics.forEach((metric, i) => {
    const row = Math.floor(i / 2);
    const col = i % 2;
    const xPos = 0.7 + col * 2.2;
    const yPos = 2.5 + row * 1.8;
    
    // 指标卡片
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: xPos, y: yPos, w: 2.0, h: 1.6,
      fill: { color: metric.color + "20" },
      line: { color: metric.color, width: 2 }
    });
    
    // 图标
    slide.addText(metric.icon, {
      x: xPos + 0.8, y: yPos + 0.2, w: 0.4, h: 0.4,
      fontSize: 20,
      align: 'center'
    });
    
    // 数据
    slide.addText(metric.data, {
      x: xPos, y: yPos + 0.6, w: 2.0, h: 0.5,
      fontSize: 28,
      bold: true,
      color: metric.color,
      align: 'center'
    });
    
    // 标题
    slide.addText(metric.title, {
      x: xPos, y: yPos + 1.1, w: 2.0, h: 0.3,
      fontSize: 11,
      bold: true,
      color: "333333",
      align: 'center'
    });
    
    // 描述
    slide.addText(metric.description, {
      x: xPos, y: yPos + 1.35, w: 2.0, h: 0.2,
      fontSize: 9,
      color: "666666",
      align: 'center'
    });
  });
  
  // 右侧：教学反思与改进
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 5.2, y: 1.8, w: 4.3, h: 4.5,
    fill: { color: "fff5e6" },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("教学反思与改进", {
    x: 5.3, y: 1.9, w: 4.1, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  // 反思要点
  const reflections = [
    {
      area: "成功经验",
      points: [
        "情境创设有效激发学习动机",
        "技术融合提升课堂互动性",
        "五育融合促进学生全面发展",
        "过程性评价更全面客观"
      ],
      color: "#4CAF50"
    },
    {
      area: "存在问题", 
      points: [
        "部分学生技术适应需要时间",
        "个性化指导资源有待丰富",
        "家校协同机制需进一步优化",
        "数据隐私保护需加强"
      ],
      color: "#F44336"
    },
    {
      area: "改进方向",
      points: [
        "开发更多分层教学资源",
        "加强教师技术应用培训",
        "完善家校数字化沟通平台",
        "建立更科学的评价体系"
      ],
      color: "#2196F3"
    }
  ];
  
  reflections.forEach((reflection, i) => {
    const yPos = 2.5 + i * 1.5;
    
    slide.addText(reflection.area, {
      x: 5.4, y: yPos, w: 4.0, h: 0.3,
      fontSize: 14,
      bold: true,
      color: reflection.color,
      align: 'left'
    });
    
    reflection.points.forEach((point, j) => {
      slide.addText(`• ${point}`, {
        x: 5.5, y: yPos + 0.35 + j * 0.3, w: 3.9, h: 0.25,
        fontSize: 9,
        color: "333333",
        lineSpacing: 4
      });
    });
  });
  
  // 底部：可持续发展路径
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.4, w: 9.0, h: 0.8,
    fill: { color: theme.bg },
    line: { color: "cccccc", width: 1 }
  });
  
  slide.addText("可持续发展路径: 数据驱动精准教研 → 技术赋能课堂创新 → 五育融合全面发展 → 家校社协同育人", {
    x: 0.6, y: 6.5, w: 8.8, h: 0.6,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  // 页脚
  slide.addText("上海小学英语教学改革 | 基于实证研究的教学改进", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };