/**
 * Slide 11: 教师专业发展 - 数字化教学能力提升
 */

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // 标题区域
  slide.addText("教师专业发展", {
    x: 1, y: 0.3, w: 8.5, h: 0.8,
    fontSize: 32,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 副标题
  slide.addText("数字化时代教师能力提升路径", {
    x: 1, y: 1.1, w: 8.5, h: 0.5,
    fontSize: 22,
    color: theme.secondary,
    align: 'center',
    italic: true
  });
  
  // 左侧：教师能力框架
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.8, w: 4.2, h: 4.5,
    fill: { color: "f8f9fa" },
    line: { color: theme.primary, width: 2 }
  });
  
  slide.addText("数字化教师能力框架", {
    x: 0.6, y: 1.9, w: 4.0, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.primary,
    align: 'center'
  });
  
  // 能力维度轮状图
  const abilities = [
    { name: "技术应用", level: 85, color: theme.primary },
    { name: "教学设计", level: 90, color: theme.secondary },
    { name: "数据素养", level: 75, color: theme.accent },
    { name: "创新思维", level: 80, color: theme.light },
    { name: "协同育人", level: 70, color: "#9C27B0" }
  ];
  
  const centerX = 2.6;
  const centerY = 4.0;
  const radius = 1.5;
  
  // 绘制雷达图背景
  abilities.forEach((ability, i) => {
    const angle = (i / abilities.length) * 2 * Math.PI;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    
    // 轴线
    slide.addShape(pres.ShapeType.LINE, {
      x: centerX, y: centerY, w: x - centerX, h: y - centerY,
      line: { color: "cccccc", width: 1 }
    });
    
    // 能力点标签
    slide.addText(ability.name, {
      x: x - 0.5, y: y - 0.2, w: 1.0, h: 0.4,
      fontSize: 10,
      bold: true,
      color: ability.color,
      align: 'center'
    });
    
    // 能力值
    const levelRadius = radius * (ability.level / 100);
    const levelX = centerX + levelRadius * Math.cos(angle);
    const levelY = centerY + levelRadius * Math.sin(angle);
    
    slide.addShape(pres.ShapeType.ELLIPSE, {
      x: levelX - 0.1, y: levelY - 0.1, w: 0.2, h: 0.2,
      fill: { color: ability.color },
      line: { color: "ffffff", width: 1 }
    });
    
    slide.addText(`${ability.level}%`, {
      x: levelX - 0.3, y: levelY + 0.1, w: 0.6, h: 0.2,
      fontSize: 8,
      color: ability.color,
      align: 'center'
    });
  });
  
  // 连接能力点形成雷达图
  const points = abilities.map((ability, i) => {
    const angle = (i / abilities.length) * 2 * Math.PI;
    const levelRadius = radius * (ability.level / 100);
    return {
      x: centerX + levelRadius * Math.cos(angle),
      y: centerY + levelRadius * Math.sin(angle)
    };
  });
  
  // 绘制雷达图填充（多边形）
  slide.addShape(pres.ShapeType.TRIANGLE, {
    x: points[0].x, y: points[0].y, w: 0.1, h: 0.1,
    fill: { color: theme.primary + "40" },
    line: { color: theme.primary, width: 2 }
  });
  
  // 右侧：专业发展路径
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 5.0, y: 1.8, w: 4.5, h: 4.5,
    fill: { color: "f0f7ff" },
    line: { color: theme.secondary, width: 2 }
  });
  
  slide.addText("专业发展路径", {
    x: 5.1, y: 1.9, w: 4.3, h: 0.5,
    fontSize: 18,
    bold: true,
    color: theme.secondary,
    align: 'center'
  });
  
  // 发展阶梯
  const stages = [
    {
      level: "入门级",
      focus: "基础技术操作",
      activities: ["平台注册使用", "资源查找下载", "基础课件制作"],
      color: "#BBDEFB"
    },
    {
      level: "熟练级", 
      focus: "融合应用创新",
      activities: ["技术支持的教学设计", "数据驱动学情分析", "个性化资源开发"],
      color: "#64B5F6"
    },
    {
      level: "专家级",
      focus: "引领辐射带动",
      activities: ["课题研究与论文", "校本研修组织", "区域示范引领"],
      color: "#1976D2"
    },
    {
      level: "研究级",
      focus: "理论实践创新",
      activities: ["教学模式创新", "学术成果转化", "政策标准制定"],
      color: "#0D47A1"
    }
  ];
  
  stages.forEach((stage, i) => {
    const yPos = 2.5 + i * 1.1;
    
    // 阶梯卡片
    slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
      x: 5.2, y: yPos, w: 4.1, h: 1.0,
      fill: { color: stage.color },
      line: { color: "ffffff", width: 2 }
    });
    
    // 级别
    slide.addText(stage.level, {
      x: 5.3, y: yPos + 0.1, w: 1.0, h: 0.3,
      fontSize: 14,
      bold: true,
      color: "ffffff",
      align: 'left'
    });
    
    // 重点
    slide.addText(stage.focus, {
      x: 6.4, y: yPos + 0.1, w: 2.8, h: 0.3,
      fontSize: 12,
      italic: true,
      color: "ffffff",
      align: 'right'
    });
    
    // 活动
    stage.activities.forEach((activity, j) => {
      slide.addText(`• ${activity}`, {
        x: 5.3, y: yPos + 0.4 + j * 0.2, w: 3.9, h: 0.2,
        fontSize: 9,
        color: "ffffff",
        lineSpacing: 4
      });
    });
  });
  
  // 底部：支持体系
  slide.addShape(pres.ShapeType.ROUNDED_RECTANGLE, {
    x: 0.5, y: 6.4, w: 9.0, h: 0.8,
    fill: { color: theme.bg },
    line: { color: "cccccc", width: 1 }
  });
  
  slide.addText("支持体系: 市-区-校三级研修 + 校企合作培训 + 名师工作室引领 + 在线学习共同体", {
    x: 0.6, y: 6.5, w: 8.8, h: 0.6,
    fontSize: 10,
    color: theme.primary,
    align: 'center'
  });
  
  // 页脚
  slide.addText("上海教师专业发展 | 数字化转型背景下的能力建设", {
    x: 0, y: 7.0, w: "100%", h: 0.3,
    fontSize: 10,
    color: "999999",
    align: 'center'
  });
  
  return slide;
}

module.exports = { createSlide };