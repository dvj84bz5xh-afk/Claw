// slides/slide-12.js
// Summary

const slideConfig = {
  title: "总结与启示",
  subtitle: "素养导向 × 技术赋能：迈向小学英语教学新样态",
  pageNumber: 12,
  content: {
    left: {
      title: "📌 形成的核心共识",
      items: [
        "素养导向的单元整体教学，核心在于以“大观念”统整教学内容，以“真情境”驱动学习活动，以“促发展”设计评价体系",
        "技术赋能的关键在于“融合”而非“叠加”，应选择最能解决教学难点、提升学习体验的工具，避免为技术而技术",
        "学生中心、学为中心的课堂，需要教师从“讲授者”转变为“设计者”、“引导者”与“协作者”"
      ]
    },
    right: {
      title: "🚀 未来行动方向",
      sections: [
        {
          title: "1. 深化“设计—实践—反思”循环",
          text: "以本次实践为起点，教研组将持续开展课例研究，迭代优化教学设计，形成可推广的单元教学案例库"
        },
        {
          title: "2. 构建校际协作网络",
          text: "利用数字平台，开展跨校集体备课、观课议课，共享优质资源，共同破解教学难题"
        },
        {
          title: "3. 探索素养评价新范式",
          text: "依托技术工具，尝试对语言能力、文化意识、思维品质、学习能力进行更科学、更过程性的追踪与评估"
        },
        {
          title: "4. 赋能教师专业发展",
          text: "开展针对性的技术工作坊、教学设计工作坊，提升教师融合技术与素养的教学设计能力"
        }
      ]
    }
  }
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // Title
  slide.addText(slideConfig.title, {
    x: 1, y: 0.5, w: 8, h: 0.8,
    fontSize: 28, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  // Subtitle
  slide.addText(slideConfig.subtitle, {
    x: 1, y: 1.3, w: 8, h: 0.5,
    fontSize: 18, color: theme.secondary,
    fontFace: 'Microsoft YaHei'
  });
  
  // Left column: Consensus
  slide.addText(slideConfig.content.left.title, {
    x: 0.5, y: 2.2, w: 4, h: 0.6,
    fontSize: 20, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  const leftItems = slideConfig.content.left.items.map(item => `• ${item}`).join('\n');
  slide.addText(leftItems, {
    x: 0.7, y: 2.8, w: 3.8, h: 2.5,
    fontSize: 14, color: '333333',
    fontFace: 'Microsoft YaHei',
    bullet: true, bulletIndent: 0.3
  });
  
  // Right column: Future directions
  slide.addText(slideConfig.content.right.title, {
    x: 5, y: 2.2, w: 4, h: 0.6,
    fontSize: 20, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  let yOffset = 2.8;
  slideConfig.content.right.sections.forEach(section => {
    slide.addText(section.title, {
      x: 5.2, y: yOffset, w: 3.8, h: 0.5,
      fontSize: 16, bold: true, color: theme.secondary,
      fontFace: 'Microsoft YaHei'
    });
    yOffset += 0.5;
    
    slide.addText(section.text, {
      x: 5.4, y: yOffset, w: 3.6, h: 1,
      fontSize: 13, color: '555555',
      fontFace: 'Microsoft YaHei'
    });
    yOffset += 1.2;
  });
  
  // Visual element: Cycle diagram
  slide.addShape(pres.ShapeType.ellipse, {
    x: 3, y: 5.2, w: 3, h: 1.8,
    fill: { color: 'FFFFFF' },
    line: { color: theme.primary, width: 3, dashType: 'dash' }
  });
  
  const cyclePoints = [
    { x: 4.5, y: 5.3, label: "设计", angle: 0 },
    { x: 5.2, y: 6, label: "实践", angle: 90 },
    { x: 4.5, y: 6.7, label: "反思", angle: 180 },
    { x: 3.8, y: 6, label: "优化", angle: 270 }
  ];
  
  cyclePoints.forEach(point => {
    slide.addShape(pres.ShapeType.roundRect, {
      x: point.x - 0.4, y: point.y - 0.2, w: 0.8, h: 0.4,
      fill: { color: theme.light },
      line: { color: theme.primary }
    });
    slide.addText(point.label, {
      x: point.x - 0.4, y: point.y - 0.2, w: 0.8, h: 0.4,
      fontSize: 12, align: 'center', valign: 'middle',
      fontFace: 'Microsoft YaHei'
    });
  });
  
  slide.addText("持续改进循环", {
    x: 4, y: 6, w: 1, h: 0.4,
    fontSize: 12, bold: true, align: 'center',
    fontFace: 'Microsoft YaHei'
  });
  
  // Final thank you note
  slide.addText("谢谢聆听！", {
    x: 1, y: 6.8, w: 8, h: 0.6,
    fontSize: 24, bold: true, color: theme.secondary,
    align: 'center', fontFace: 'Microsoft YaHei'
  });
  
  // Page number badge
  slide.addShape(pres.ShapeType.roundRect, {
    x: 8.5, y: 6.8, w: 0.8, h: 0.4,
    fill: { color: theme.primary },
    line: { color: theme.primary }
  });
  slide.addText(`第${slideConfig.pageNumber}页`, {
    x: 8.5, y: 6.8, w: 0.8, h: 0.4,
    fontSize: 12, bold: true, color: 'FFFFFF',
    align: 'center', valign: 'middle',
    fontFace: 'Microsoft YaHei'
  });
  
  return slide;
}

module.exports = { slideConfig, createSlide };