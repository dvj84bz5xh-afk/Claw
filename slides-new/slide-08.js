/**
 * Slide 08: 课时教学设计 - 第4课时 "成果展示 - 五育少年成长计划发布会"
 * 基于上海小学英语四年级下册 Module 3 Unit 3 "Days of the week"
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("课时教学设计（第4课时）", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("成果展示 - 五育少年成长计划发布会", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 中心：发布会舞台设计
  slide.addShape(pres.ShapeType.ELLIPSE, {
    x: 2.0, y: 1.8, w: 6.0, h: 3.0,
    fill: { color: "f0f7ff" },
    line: { color: theme.primary, width: 3 }
  });
  
  slide.addText("🎤", {
    x: 4.8, y: 2.5, w: 0.5, h: 0.5,
    fontSize: 32,
    align: 'center'
  });
  
  slide.addText("五育少年成长计划\n发布会", {
    x: 2.0, y: 3.0, w: 6.0, h: 1.0,
    fontSize: 24,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 环绕的展示成果
  const showcases = [
    { text: "个人英文vlog", x: 1.0, y: 1.5, color: theme.accent },
    { text: "数字作品集", x: 1.5, y: 5.0, color: theme.secondary },
    { text: "AR计划表", x: 7.5, y: 1.5, color: theme.light },
    { text: "小组海报", x: 8.0, y: 5.0, color: theme.primary }
  ];
  
  showcases.forEach(show => {
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: show.x, y: show.y, w: 2.0, h: 0.8,
      fill: { color: show.color + "20" },
      line: { color: show.color, width: 2 }
    });
    
    slide.addText(show.text, {
      x: show.x, y: show.y + 0.2, w: 2.0, h: 0.4,
      fontSize: 12,
      bold: true,
      color: show.color,
      align: 'center'
    });
  });
  
  // 左侧：展示流程
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 2.5, w: 3.0, h: 3.5,
    fill: { color: "f8f9fa" },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("展示流程", {
    x: 0.6, y: 2.6, w: 2.8, h: 0.4,
    fontSize: 16,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  const steps = [
    "1. 暖场: 五育少年主题曲",
    "2. 开场: 主持人介绍发布会",
    "3. 展示: 学生作品轮流展示",
    "4. 互动: 现场问答与投票",
    "5. 点评: 教师与专家反馈",
    "6. 颁奖: 最佳作品表彰",
    "7. 总结: 成长计划启动"
  ];
  
  steps.forEach((step, i) => {
    slide.addText(step, {
      x: 0.7, y: 3.1 + i * 0.45, w: 2.6, h: 0.4,
      fontSize: 10,
      color: "333333"
    });
  });
  
  // 右侧：评价标准
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 6.5, y: 2.5, w: 3.0, h: 3.5,
    fill: { color: "fff5e6" },
    line: { color: theme.accent, width: 2 }
  });
  
  slide.addText("评价标准", {
    x: 6.6, y: 2.6, w: 2.8, h: 0.4,
    fontSize: 16,
    bold: true,
    color: theme.accent,
    align: 'center'
  });
  
  const criteria = [
    "✓ 语言表达准确性(30%)",
    "✓ 内容创意与设计(25%)",
    "✓ 五育融合深度(20%)",
    "✓ 技术应用水平(15%)",
    "✓ 展示表现力(10%)",
    "",
    "评价方式: 教师评分(40%) +\n同学互评(30%) + AI测评(30%)"
  ];
  
  criteria.forEach((criterion, i) => {
    slide.addText(criterion, {
      x: 6.7, y: 3.1 + i * 0.45, w: 2.6, h: 0.4,
      fontSize: i === 6 ? 9 : 10,
      color: i === 6 ? theme.primary : "333333",
      lineSpacing: i === 6 ? 4 : 0
    });
  });
  
  // 底部：技术平台支持
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.2, w: 9.0, h: 0.8,
    fill: { color: theme.bg },
    line: { color: "cccccc", width: 1 }
  });
  
  slide.addText("技术平台支持: 腾讯会议直播 + 微信小程序投票 + AI语音实时翻译 + 数字作品墙云展示 + 成长档案自动生成", {
    x: 0.6, y: 6.3, w: 8.8, h: 0.6,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  // 页脚
  slide.addText("上海小学英语 | 单元整体教学成果展示环节", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };