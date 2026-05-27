// slides/slide-10.js
// Technology Application - Homework Assistant

const slideConfig = {
  title: "技术应用展示：作业助手",
  subtitle: "拓展个性化学习空间",
  pageNumber: 10,
  content: {
    left: {
      title: "🔍 核心功能",
      items: [
        "分层作业推送：根据课堂表现数据，向不同学生推送基础巩固、能力提升或拓展探究类作业",
        "项目协作空间：为小组项目提供在线协作白板、资源库与进度跟踪工具",
        "自动批改与反馈：客观题系统自动批改，主观题提供参考答案与评分要点"
      ]
    },
    right: {
      title: "💡 应用场景示例",
      sections: [
        {
          title: "场景一：差异化作业布置",
          text: "• 学生A（掌握良好）：推送“设计英文课程表”创意任务\n• 学生B（需巩固）：推送词汇配对游戏与句型仿写练习\n• 学生C（兴趣浓厚）：推送英文短片观看与观后感写作"
        },
        {
          title: "场景二：项目协作支持",
          text: "• “完美校园日”项目小组获得专属协作空间\n• 成员可同时编辑海报草图、上传图片、添加文字\n• 教师可实时查看各小组进度，在线提供指导"
        },
        {
          title: "场景三：学习成果展示与互评",
          text: "• 学生将作业成果上传至班级作品墙\n• 同伴可点赞、评论，提出改进建议\n• 形成积极的学习共同体氛围"
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
  
  // Left column: Features
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
  
  // Right column: Scenarios
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
  
  // Visual element: Three cards representing differentiated homework
  const cards = [
    { title: "基础巩固", color: theme.light, y: 5.3 },
    { title: "能力提升", color: theme.accent, y: 5.3 },
    { title: "拓展探究", color: theme.secondary, y: 5.3 }
  ];
  
  cards.forEach((card, i) => {
    slide.addShape(pres.ShapeType.roundRect, {
      x: 1 + i * 2.5, y: card.y, w: 2, h: 1,
      fill: { color: card.color },
      line: { color: theme.primary, width: 1 }
    });
    slide.addText(card.title, {
      x: 1 + i * 2.5, y: card.y + 0.3, w: 2, h: 0.4,
      fontSize: 14, bold: true, color: '333333',
      align: 'center', fontFace: 'Microsoft YaHei'
    });
    slide.addText(i === 0 ? "词汇游戏\n句型仿写" : 
                  i === 1 ? "设计课程表\n短文阅读" : 
                  "英文短片\n观后感",
      {
        x: 1 + i * 2.5, y: card.y + 0.7, w: 2, h: 0.6,
        fontSize: 11, align: 'center', fontFace: 'Microsoft YaHei'
      });
  });
  
  slide.addText("分层作业示例", {
    x: 3.5, y: 4.8, w: 2, h: 0.4,
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