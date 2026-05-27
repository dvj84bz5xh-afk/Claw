// slides/slide-11.js
// Expert Evaluation

const slideConfig = {
  title: "专家评价与研讨共识",
  subtitle: "华东师范大学外语教学专家 王教授",
  pageNumber: 11,
  content: {
    left: {
      title: "✅ 核心肯定",
      items: [
        "理念前沿，设计系统：教学设计完整体现了素养导向，将语言学习置于有意义的文化语境与思维活动中",
        "技术融合自然有效：“三个助手”的应用紧密服务于教学目标的达成，在个性化反馈与合作学习支持方面优势显著",
        "学生中心突出：课堂观察显示学生参与度高，从被动接受到主动探究、合作创造，体现学习方式深刻转变",
        "评价改革初见成效：过程性评价与表现性任务的结合，使评价真正成为促进学习的工具"
      ]
    },
    right: {
      title: "💡 建议与深化方向",
      sections: [
        {
          title: "1. 素养发展的长效跟踪",
          text: "利用平台积累的数据，尝试对学生四大素养的发展进行纵向追踪与可视化分析，为差异化教学提供更精准依据"
        },
        {
          title: "2. 跨学科融合探索",
          text: "本单元主题可自然关联美术（设计海报）、音乐（创作校园歌曲）、德育（探讨友谊），未来可尝试与相关学科教师协同设计项目式学习"
        },
        {
          title: "3. 技术工具的适切性反思",
          text: "需进一步关注技术使用的“度”，确保技术始终服务于人际互动与深度思考，避免过度依赖或干扰"
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
  
  // Left column: Affirmations
  slide.addText(slideConfig.content.left.title, {
    x: 0.5, y: 2.2, w: 4, h: 0.6,
    fontSize: 20, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  const leftItems = slideConfig.content.left.items.map(item => `• ${item}`).join('\n');
  slide.addText(leftItems, {
    x: 0.7, y: 2.8, w: 3.8, h: 3,
    fontSize: 14, color: '333333',
    fontFace: 'Microsoft YaHei',
    bullet: true, bulletIndent: 0.3
  });
  
  // Right column: Suggestions
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
  
  // Visual element: Balance scale (technology vs. interaction)
  slide.addShape(pres.ShapeType.triangle, {
    x: 4, y: 5.5, w: 0.5, h: 0.3,
    fill: { color: '888888' },
    line: { color: '888888' }
  });
  
  slide.addShape(pres.ShapeType.line, {
    x: 3.5, y: 5.8, w: 2, h: 0,
    line: { color: '888888', width: 2 }
  });
  
  slide.addShape(pres.ShapeType.rect, {
    x: 3, y: 5.8, w: 0.8, h: 0.5,
    fill: { color: theme.primary },
    line: { color: theme.primary }
  });
  slide.addText("技术", {
    x: 3, y: 5.9, w: 0.8, h: 0.3,
    fontSize: 12, align: 'center', fontFace: 'Microsoft YaHei'
  });
  
  slide.addShape(pres.ShapeType.rect, {
    x: 5.2, y: 5.8, w: 0.8, h: 0.5,
    fill: { color: theme.secondary },
    line: { color: theme.secondary }
  });
  slide.addText("人际互动", {
    x: 5.2, y: 5.9, w: 0.8, h: 0.3,
    fontSize: 12, align: 'center', fontFace: 'Microsoft YaHei'
  });
  
  slide.addText("保持平衡", {
    x: 4, y: 6.4, w: 1, h: 0.4,
    fontSize: 12, bold: true, align: 'center',
    fontFace: 'Microsoft YaHei'
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