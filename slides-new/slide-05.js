/**
 * Slide 05: 课时教学设计 - 第1课时 "情境导入 - 五育少年Peter获奖采访"
 * 基于上海小学英语四年级下册 Module 3 Unit 3 "Days of the week"
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("课时教学设计（第1课时）", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("情境导入 - 五育少年Peter获奖采访", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 左侧：教学设计四要素卡片
  const cardWidth = 3.8;
  const cardHeight = 1.2;
  
  // 卡片1: 教学目标
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 2.0, w: cardWidth, h: cardHeight,
    fill: { color: theme.bg },
    line: { color: theme.primary, width: 2 }
  });
  
  slide.addText("教学目标", {
    x: 0.6, y: 2.1, w: cardWidth - 0.2, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  slide.addText("1. 能听懂、认读、会说: Monday-Friday\n2. 能在采访情境中询问日程安排\n3. 了解优秀学生一周时间规划", {
    x: 0.6, y: 2.5, w: cardWidth - 0.2, h: cardHeight - 0.4,
    fontSize: 12,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 卡片2: 教学过程
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 4.7, y: 2.0, w: cardWidth, h: cardHeight,
    fill: { color: theme.bg },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("教学过程", {
    x: 4.8, y: 2.1, w: cardWidth - 0.2, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  slide.addText("① 播放Peter获奖新闻视频(30s)\n② 创设采访情境，师生角色扮演\n③ 小组对话练习：My week plan\n④ 展示与互评", {
    x: 4.8, y: 2.5, w: cardWidth - 0.2, h: cardHeight - 0.4,
    fontSize: 12,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 卡片3: 技术应用
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 3.8, w: cardWidth, h: cardHeight,
    fill: { color: theme.bg },
    line: { color: theme.accent, width: 2 }
  });
  
  slide.addText("技术应用", {
    x: 0.6, y: 3.9, w: cardWidth - 0.2, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.accent,
    align: 'center'
  });
  
  slide.addText("• 数字人主播播报Peter事迹\n• AI语音测评学生发音\n• AR日历交互学习星期\n• 云笔记记录学习心得", {
    x: 0.6, y: 4.3, w: cardWidth - 0.2, h: cardHeight - 0.4,
    fontSize: 12,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 卡片4: 预期效果
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 4.7, y: 3.8, w: cardWidth, h: cardHeight,
    fill: { color: theme.bg },
    line: { color: theme.light, width: 2 }
  });
  
  slide.addText("预期效果", {
    x: 4.8, y: 3.9, w: cardWidth - 0.2, h: 0.4,
    fontSize: 18,
    bold: true,
    color: theme.light,
    align: 'center'
  });
  
  slide.addText("① 90%学生能正确说出星期名称\n② 学生建立时间规划初步意识\n③ 激发学生争当五育少年热情\n④ 为后续单元学习奠定基础", {
    x: 4.8, y: 4.3, w: cardWidth - 0.2, h: cardHeight - 0.4,
    fontSize: 12,
    lineSpacing: 6,
    color: "333333"
  });
  
  // 底部示意图
  slide.addText("教学设计示意图：从情境创设到素养达成", {
    x: 0.5, y: 5.5, w: 9, h: 0.4,
    fontSize: 14,
    color: "666666",
    italic: true
  });
  
  // 流程图元素
  const flowX = [1, 3.5, 6, 8];
  const flowLabels = ["情境导入", "语言输入", "技能训练", "素养提升"];
  const flowColors = [theme.primary, theme.secondary, theme.accent, theme.light];
  
  for (let i = 0; i < 4; i++) {
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: flowX[i], y: 6.0, w: 1.8, h: 0.6,
      fill: { color: flowColors[i] },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(flowLabels[i], {
      x: flowX[i], y: 6.1, w: 1.8, h: 0.4,
      fontSize: 12,
      bold: true,
      color: "ffffff",
      align: 'center'
    });
    
    // 连接箭头
    if (i < 3) {
      slide.addShape(pres.SHAPE_TYPE.TRIANGLE, {
        x: flowX[i] + 1.9, y: 6.2, w: 0.3, h: 0.2,
        fill: { color: "666666" },
        rotate: 0
      });
    }
  }
  
  // 页脚
  slide.addText("上海小学英语 | 四年级下册 Module 3 Unit 3 'Days of the week'", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };