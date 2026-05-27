// slides/slide-05.js
// Teaching Activity - Listening & Reading (Language Construction)

const slideConfig = {
  title: "教学活动设计：语言建构",
  subtitle: "课时2：核心句型与词汇学习",
  pageNumber: 5,
  content: {
    left: {
      title: "🎯 本课时目标",
      items: [
        "掌握核心词汇：subject, Chinese, maths, English, PE, art, music",
        "运用核心句型进行简单对话：",
        "  • What subjects do you have?",
        "  • I have... / I don't have...",
        "  • My favourite subject is... because..."
      ]
    },
    right: {
      title: "📝 活动流程设计",
      sections: [
        {
          title: "1. 情境复现与词汇输入 (10分钟)",
          text: "• 观看校园生活短片，聚焦课程场景\n• 利用单词卡片进行听说训练，结合图片释义\n• 小组竞赛：快速指认课程单词"
        },
        {
          title: "2. 句型感知与模仿 (15分钟)",
          text: "• 教师示范对话：询问与回答课程喜好\n• 学生跟读录音，利用AI语音助手纠正发音\n• 同桌配对练习，替换关键词进行模仿对话"
        },
        {
          title: "3. 游戏化巩固与应用 (15分钟)",
          text: "• “课程调查员”活动：采访3位同学，记录他们的课程表\n• 使用句型：“What subjects do you have on Monday?”\n• 小组汇总调查结果，用Padlet展示“班级最爱课程”"
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
    x: 0.7, y: 2.8, w: 3.8, h: 3,
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
  
  // Decorative element
  slide.addShape(pres.ShapeType.rect, {
    x: 4.8, y: 2, w: 0.1, h: 4,
    fill: { color: theme.accent },
    line: { color: theme.accent }
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