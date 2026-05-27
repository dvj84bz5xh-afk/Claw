// slide-08.js - Technology Application - Teaching Assistant
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 8,
  title: '三、技术应用展示 - 教学助手',
  subtitle: '个性化学习支持平台',
  features: [
    {
      title: '资源精准推送',
      description: '根据学生学情推送差异化学习资源',
      examples: ['动画视频', '互动游戏', '分层练习']
    },
    {
      title: '思维可视化工具',
      description: '实时生成思维导图，构建知识网络',
      examples: ['Peter一周活动思维导图', '核心句型结构图']
    },
    {
      title: '互动协作平台',
      description: '支持小组在线协作，促进生生互动',
      examples: ['实时讨论区', '协作任务板', '成果共享']
    }
  ],
  benefits: [
    '从统一化教学走向个性化学习',
    '从教师中心走向学生中心',
    '从知识传授走向素养培养'
  ]
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // Title
  slide.addText(slideConfig.title, {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 24,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true
  });
  
  // Subtitle
  slide.addText(slideConfig.subtitle, {
    x: 0.5, y: 1.2, w: 9, h: 0.5,
    fontSize: 20,
    fontFace: "Microsoft YaHei",
    color: theme.secondary,
    italic: true
  });
  
  // Features
  const featureWidth = 2.8;
  const featureHeight = 2.2;
  const featureGap = 0.3;
  
  slideConfig.features.forEach((feature, index) => {
    const x = 0.5 + (index * (featureWidth + featureGap));
    const y = 1.8;
    
    // Feature card
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: featureWidth, h: featureHeight,
      fill: { color: index === 1 ? theme.light : "f8f9fa" },
      line: { color: theme.accent, width: 1 },
      rectRadius: 0.1
    });
    
    // Feature title
    slide.addText(feature.title, {
      x: x + 0.2, y: y + 0.2, w: featureWidth - 0.4, h: 0.4,
      fontSize: 16,
      fontFace: "Microsoft YaHei",
      color: theme.primary,
      bold: true,
      align: "center",
      valign: "middle"
    });
    
    // Description
    slide.addText(feature.description, {
      x: x + 0.2, y: y + 0.7, w: featureWidth - 0.4, h: 0.5,
      fontSize: 14,
      fontFace: "Microsoft YaHei",
      color: "333333",
      align: "center"
    });
    
    // Examples
    slide.addText('应用示例：', {
      x: x + 0.2, y: y + 1.3, w: featureWidth - 0.4, h: 0.3,
      fontSize: 12,
      fontFace: "Microsoft YaHei",
      color: theme.secondary,
      bold: true
    });
    
    feature.examples.forEach((example, exIndex) => {
      slide.addText(`• ${example}`, {
        x: x + 0.3, y: y + 1.6 + (exIndex * 0.25), w: featureWidth - 0.6, h: 0.2,
        fontSize: 11,
        fontFace: "Microsoft YaHei",
        color: "555555"
      });
    });
  });
  
  // Benefits section
  slide.addText('教学变革：', {
    x: 0.5, y: 4.2, w: 9, h: 0.4,
    fontSize: 18,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true
  });
  
  slideConfig.benefits.forEach((benefit, index) => {
    const y = 4.6 + (index * 0.35);
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: y - 0.05, w: 0.2, h: 0.2,
      fill: { color: theme.secondary },
      rectRadius: 0.05
    });
    
    slide.addText(`${index + 1}`, {
      x: 0.7, y: y - 0.05, w: 0.2, h: 0.2,
      fontSize: 12,
      fontFace: "Arial",
      color: "FFFFFF",
      bold: true,
      align: "center",
      valign: "middle"
    });
    
    slide.addText(benefit, {
      x: 1, y: y, w: 8, h: 0.3,
      fontSize: 16,
      fontFace: "Microsoft YaHei",
      color: "333333",
      bold: true
    });
  });
  
  // Page number badge
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("8", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12,
    fontFace: "Arial",
    color: "FFFFFF",
    bold: true,
    align: "center",
    valign: "middle"
  });
  
  return slide;
}

// Standalone preview
if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "2ec4b6",
    secondary: "ff9f1c",
    accent: "ffbf69",
    light: "cbf3f0",
    bg: "ffffff"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "slide-08-preview.pptx" });
}

module.exports = { createSlide, slideConfig };