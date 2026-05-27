/**
 * Slide 07: 课时教学设计 - 第3课时 "技能训练 - 我的星期我做主"
 * 基于上海小学英语四年级下册 Module 3 Unit 3 "Days of the week"
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("课时教学设计（第3课时）", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("技能训练 - 我的星期我做主", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 左侧：技能训练金字塔
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.8, w: 4.2, h: 4.5,
    fill: { color: "f9f9f9" },
    line: { color: theme.primary, width: 2 }
  });
  
  slide.addText("技能训练金字塔模型", {
    x: 0.6, y: 1.9, w: 4.0, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 金字塔层级
  const levels = [
    { name: "创造应用", color: theme.accent, y: 5.0, height: 0.8 },
    { name: "迁移拓展", color: theme.secondary, y: 4.2, height: 0.8 },
    { name: "理解运用", color: theme.light, y: 3.4, height: 0.8 },
    { name: "模仿练习", color: "#a7e6ff", y: 2.6, height: 0.8 },
    { name: "感知认知", color: "#d9f2ff", y: 1.8, height: 0.8 }
  ];
  
  for (let i = 0; i < levels.length; i++) {
    const level = levels[i];
    const width = 3.0 + i * 0.4;
    const xPos = 1.1 + (4.2 - width) / 2;
    
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: xPos, y: level.y, w: width, h: level.height,
      fill: { color: level.color },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(level.name, {
      x: xPos, y: level.y + 0.2, w: width, h: 0.4,
      fontSize: 12,
      bold: true,
      color: i < 2 ? "ffffff" : "333333",
      align: 'center'
    });
  }
  
  // 箭头连接
  for (let i = 0; i < levels.length - 1; i++) {
    slide.addShape(pres.ShapeType.TRIANGLE, {
      x: 3.0, y: levels[i].y + levels[i].height - 0.1, w: 0.3, h: 0.2,
      fill: { color: "666666" },
      rotate: 0
    });
  }
  
  // 右侧：具体活动设计
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 5.0, y: 1.8, w: 4.5, h: 4.5,
    fill: { color: "f5faff" },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("具体活动设计", {
    x: 5.1, y: 1.9, w: 4.3, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  // 活动卡片
  const activities = [
    {
      title: "感知认知",
      items: ["观看Peter榜样视频", "听星期词汇音频", "跟读模仿"],
      color: "#d9f2ff"
    },
    {
      title: "模仿练习", 
      items: ["AI语音测评", "AR星期卡片配对", "情景对话练习"],
      color: "#a7e6ff"
    },
    {
      title: "理解运用",
      items: ["完成计划表填空", "小组对话问答", "时间表达练习"],
      color: theme.light
    },
    {
      title: "迁移拓展",
      items: ["设计个人计划表", "模拟采访同学", "创作星期歌曲"],
      color: theme.secondary
    },
    {
      title: "创造应用",
      items: ["制作数字作品集", "录制英文vlog", "展示五育规划"],
      color: theme.accent
    }
  ];
  
  for (let i = 0; i < activities.length; i++) {
    const yPos = 2.5 + i * 0.85;
    
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: 5.2, y: yPos, w: 4.1, h: 0.75,
      fill: { color: activities[i].color },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(activities[i].title, {
      x: 5.3, y: yPos + 0.1, w: 1.0, h: 0.25,
      fontSize: 10,
      bold: true,
      color: i < 2 ? "333333" : "ffffff",
      align: 'left'
    });
    
    slide.addText(activities[i].items.join(" | "), {
      x: 6.4, y: yPos + 0.1, w: 2.8, h: 0.55,
      fontSize: 9,
      color: i < 2 ? "555555" : "ffffff",
      align: 'left'
    });
  }
  
  // 底部：评价方式
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.4, w: 9.0, h: 0.8,
    fill: { color: theme.bg },
    line: { color: "cccccc", width: 1 }
  });
  
  slide.addText("评价方式: 过程性评价(课堂表现+AI测评) + 成果性评价(数字作品+展示分享) + 发展性评价(进步轨迹+自我反思)", {
    x: 0.6, y: 6.5, w: 8.8, h: 0.6,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  // 页脚
  slide.addText("上海小学英语 | 核心素养：学习能力 + 思维品质", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };