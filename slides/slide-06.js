// slides/slide-06.js
// Teaching Activity - Language Exploration (Deep Inquiry)

const slideConfig = {
  title: "教学活动设计：深入探究",
  subtitle: "课时3：文化比较与思维发展",
  pageNumber: 6,
  content: {
    left: {
      title: "🎯 本课时目标",
      items: [
        "阅读关于中英小学课程表的短文，获取关键信息",
        "通过对比分析，理解文化差异，培养开放态度",
        "运用批判性思维，讨论“理想课程表”的构成要素"
      ]
    },
    right: {
      title: "📝 活动流程设计",
      sections: [
        {
          title: "1. 阅读输入与信息提取 (15分钟)",
          text: "• 默读短文《A School Day in the UK》，完成信息表填空\n• 小组合作，使用“寻读(scanning)”策略快速定位信息\n• 教师引导提炼关键词：forest school, drama, assembly"
        },
        {
          title: "2. 文化比较与讨论 (15分钟)",
          text: "• 对比中英课程表，发现异同点，填写维恩图\n• 引导性问题：\"Why do British schools have forest school?\"\n• 小组分享观点，教师总结文化差异的合理性"
        },
        {
          title: "3. 创造性思维任务 (10分钟)",
          text: "• 设计“我的理想课程表”，可融合中英特色\n• 书面或口头阐述设计理由，使用句型：\"I would add... because...\"\n• 优秀设计展示，同伴互评"
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
  
  // Left column: Objectives
  slide.addText(slideConfig.content.left.title, {
    x: 0.5, y: 2.2, w: 4, h: 0.6,
    fontSize: 20, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  const leftItems = slideConfig.content.left.items.map(item => `• ${item}`).join('\n');
  slide.addText(leftItems, {
    x: 0.7, y: 2.8, w: 3.8, h: 2.5,
    fontSize: 16, color: '333333',
    fontFace: 'Microsoft YaHei',
    bullet: true, bulletIndent: 0.3
  });
  
  // Right column: Process
  slide.addText(slideConfig.content.right.title, {
    x: 5, y: 2.2, w: 4, h: 0.6,
    fontSize: 20, bold: true, color: theme.primary,
    fontFace: 'Microsoft YaHei'
  });
  
  let yOffset = 2.8;
  slideConfig.content.right.sections.forEach(section => {
    slide.addText(section.title, {
      x: 5.2, y: yOffset, w: 3.8, h: 0.5,
      fontSize: 18, bold: true, color: theme.secondary,
      fontFace: 'Microsoft YaHei'
    });
    yOffset += 0.5;
    
    slide.addText(section.text, {
      x: 5.4, y: yOffset, w: 3.6, h: 1,
      fontSize: 14, color: '555555',
      fontFace: 'Microsoft YaHei'
    });
    yOffset += 1.2;
  });
  
  // Visual element: Venn diagram representation
  slide.addShape(pres.ShapeType.ellipse, {
    x: 2, y: 5, w: 2, h: 1.5,
    fill: { color: theme.light },
    line: { color: theme.primary, width: 2 }
  });
  slide.addText("中国课程", {
    x: 2.5, y: 5.5, w: 1, h: 0.5,
    fontSize: 12, bold: true, color: theme.primary,
    align: 'center', fontFace: 'Microsoft YaHei'
  });
  
  slide.addShape(pres.ShapeType.ellipse, {
    x: 4, y: 5, w: 2, h: 1.5,
    fill: { color: theme.accent },
    line: { color: theme.secondary, width: 2 }
  });
  slide.addText("英国课程", {
    x: 4.5, y: 5.5, w: 1, h: 0.5,
    fontSize: 12, bold: true, color: theme.secondary,
    align: 'center', fontFace: 'Microsoft YaHei'
  });
  
  slide.addText("重叠区：\n体育、艺术、数学", {
    x: 3.5, y: 5.8, w: 1, h: 0.6,
    fontSize: 10, color: '333333',
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