/**
 * Slide 06: 课时教学设计 - 第2课时 "语言输入 - Peter的星期计划表"
 * 基于上海小学英语四年级下册 Module 3 Unit 3 "Days of the week"
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("课时教学设计（第2课时）", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("语言输入 - Peter的星期计划表", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 左侧：Peter的星期计划表
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.8, w: 4.0, h: 4.5,
    fill: { color: "f8f9fa" },
    line: { color: theme.primary, width: 3 }
  });
  
  slide.addText("Peter's Weekly Schedule", {
    x: 0.6, y: 1.9, w: 3.8, h: 0.5,
    fontSize: 20,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 星期表格
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const activities = [
    "Morning: English class\nAfternoon: Sports club",
    "Morning: Math class\nAfternoon: Art workshop",
    "Morning: Science lab\nAfternoon: Music practice",
    "Morning: Coding class\nAfternoon: Team project",
    "Morning: Review week\nAfternoon: Community service"
  ];
  
  for (let i = 0; i < 5; i++) {
    const yPos = 2.5 + i * 0.8;
    
    // 星期标签
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: 0.7, y: yPos, w: 1.0, h: 0.7,
      fill: { color: i % 2 === 0 ? theme.light : "ffebcc" },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(days[i], {
      x: 0.7, y: yPos + 0.1, w: 1.0, h: 0.5,
      fontSize: 12,
      bold: true,
      color: "333333",
      align: 'center'
    });
    
    // 活动内容
    slide.addText(activities[i], {
      x: 1.9, y: yPos + 0.1, w: 2.2, h: 0.7,
      fontSize: 10,
      lineSpacing: 4,
      color: "555555"
    });
  }
  
  // 右侧：教学要点分析
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 5.0, y: 1.8, w: 4.5, h: 2.2,
    fill: { color: "e8f4f8" },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("语言输入要点", {
    x: 5.1, y: 1.9, w: 4.3, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  slide.addText("1. 核心词汇\n   • Days of the week (Monday-Friday)\n   • Daily activities verbs\n2. 句型结构\n   • On Monday, I have...\n   • What do you do on...?\n3. 语法要点\n   • 时间介词 on 的用法\n   • 一般现在时表达习惯", {
    x: 5.2, y: 2.4, w: 4.1, h: 1.5,
    fontSize: 11,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 右侧下部：教学活动设计
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 5.0, y: 4.2, w: 4.5, h: 2.1,
    fill: { color: "f0f7ff" },
    line: { color: theme.accent, width: 2 }
  });
  
  slide.addText("教学活动设计", {
    x: 5.1, y: 4.3, w: 4.3, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.accent,
    align: 'center'
  });
  
  slide.addText("① 听力训练: 听Peter采访音频填空\n② 模仿朗读: AI语音测评纠正发音\n③ 情境对话: 小组讨论自己的一周计划\n④ 书写练习: 完成个人星期计划表\n⑤ 展示分享: 数字作品墙展示成果", {
    x: 5.2, y: 4.8, w: 4.1, h: 1.5,
    fontSize: 11,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 底部：技术整合亮点
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.4, w: 9.0, h: 0.8,
    fill: { color: theme.bg },
    line: { color: "cccccc", width: 1 }
  });
  
  slide.addText("技术整合亮点: AI语音测评系统实时反馈发音准确度 | AR交互式星期计划表让学生身临其境 | 云协作平台分享个人计划", {
    x: 0.6, y: 6.5, w: 8.8, h: 0.6,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  // 页脚
  slide.addText("上海小学英语 | 核心素养：语言能力 + 思维品质", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };