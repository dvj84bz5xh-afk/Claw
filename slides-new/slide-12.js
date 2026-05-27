/**
 * Slide 12: 专家评价与共识 - 华东师范大学专家反馈
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("专家评价与共识", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("华东师范大学外语教学专家团队评析", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 专家介绍区域
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.8, w: 4.0, h: 1.5,
    fill: { color: "e8f4f8" },
    line: { color: theme.primary, width: 2 }
  });
  
  slide.addText("🏆", {
    x: 0.8, y: 2.0, w: 0.6, h: 0.6,
    fontSize: 32,
    align: 'center'
  });
  
  slide.addText("王教授", {
    x: 1.5, y: 2.0, w: 2.8, h: 0.4,
    fontSize: 20,
    bold: true,
    color: theme.primary,
    align: 'left'
  });
  
  slide.addText("华东师范大学外语学院\n课程与教学论专家", {
    x: 1.5, y: 2.4, w: 2.8, h: 0.8,
    fontSize: 12,
    color: "555555",
    lineSpacing: 6
  });
  
  // 核心评价区域
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 3.5, w: 9.0, h: 2.8,
    fill: { color: "fff9e6" },
    line: { color: theme.secondary, width: 3 }
  });
  
  slide.addText("核心评价要点", {
    x: 0.6, y: 3.6, w: 8.8, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  // 评价要点卡片
  const evaluations = [
    {
      title: "理念先进性",
      content: "充分体现核心素养导向，符合《义务教育英语课程标准（2025修订版）》要求，将语言学习与五育融合有机结合。",
      icon: "💡"
    },
    {
      title: "设计科学性",
      content: "单元整体教学设计逻辑清晰，四课时安排层层递进，从情境导入到成果展示形成完整闭环。",
      icon: "📐"
    },
    {
      title: "技术适切性",
      content: "三个助手平台应用恰到好处，技术为教学服务而非炫技，AR/AI等新技术有效支持学习目标达成。",
      icon: "💻"
    },
    {
      title: "可推广性",
      content: "模式可在上海及其他地区推广，提供了可复制的数字化转型路径，为一线教师提供实用参考。",
      icon: "🚀"
    }
  ];
  
  evaluations.forEach((evaluation, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const xPos = 0.7 + col * 4.5;
    const yPos = 4.1 + row * 1.2;
    
    // 卡片
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: xPos, y: yPos, w: 4.3, h: 1.1,
      fill: { color: i % 2 === 0 ? theme.bg : "f0f7ff" },
      line: { color: theme.light, width: 1 }
    });
    
    // 图标
    slide.addText(evaluation.icon, {
      x: xPos + 0.2, y: yPos + 0.1, w: 0.4, h: 0.4,
      fontSize: 16,
      align: 'center'
    });
    
    // 标题
    slide.addText(evaluation.title, {
      x: xPos + 0.7, y: yPos + 0.1, w: 3.4, h: 0.3,
      fontSize: 14,
      bold: true,
      color: theme.primary,
      align: 'left'
    });
    
    // 内容
    slide.addText(evaluation.content, {
      x: xPos + 0.7, y: yPos + 0.4, w: 3.4, h: 0.7,
      fontSize: 9,
      color: "333333",
      lineSpacing: 4
    });
  });
  
  // 专家共识区域
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 4.7, y: 1.8, w: 4.8, h: 1.5,
    fill: { color: "f0f0f0" },
    line: { color: theme.accent, width: 2 }
  });
  
  slide.addText("专家共识", {
    x: 4.8, y: 1.9, w: 4.6, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.accent,
    align: 'center'
  });
  
  slide.addText("该教学设计代表了上海小学英语\n数字化转型的前沿探索，为全国\n提供了可借鉴的范式。", {
    x: 4.9, y: 2.3, w: 4.4, h: 0.9,
    fontSize: 14,
    color: "333333",
    align: 'center',
    lineSpacing: 8
  });
  
  // 推广应用建议
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.4, w: 9.0, h: 1.0,
    fill: { color: "e8f5e9" },
    line: { color: "#4CAF50", width: 2 }
  });
  
  slide.addText("推广应用建议", {
    x: 0.6, y: 6.5, w: 8.8, h: 0.3,
    fontSize: 16,
    bold: true,
    color: "#4CAF50",
    align: 'center'
  });
  
  slide.addText("1. 纳入上海市教师培训课程 | 2. 编写教学案例集推广 | 3. 建立区域教研共同体 | 4. 开展跨省市交流展示", {
    x: 0.6, y: 6.8, w: 8.8, h: 0.6,
    fontSize: 11,
    color: "333333",
    align: 'center'
  });
  
  // 页脚
  slide.addText("谢谢观看 | 素养导向下的小学英语单元整体教学设计", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  slide.addText("上海市徐汇区教育学院 2026年4月", {
    x: 0, y: 7.3, w: "100%", h: 0.3,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };