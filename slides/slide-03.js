// slide-03.js - Unit Objectives
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 3,
  title: '一、单元目标解读',
  subtitle: '四年级下册 Module 3 Unit 3 Days of the week',
  objectives: [
    {
      category: '语言能力',
      items: [
        '掌握一周七天的英文表达',
        '学会用频度副词描述日常活动',
        '能听懂、会说核心句型：On Monday, Peter plays basketball.'
      ]
    },
    {
      category: '文化意识', 
      items: [
        '理解中西方时间管理观念的差异',
        '培养守时意识和时间规划能力',
        '认同健康生活习惯的重要性'
      ]
    },
    {
      category: '思维品质',
      items: [
        '通过对比分析频度副词的差异',
        '发展信息筛选和逻辑表达能力',
        '在任务驱动下培养创造性思维'
      ]
    },
    {
      category: '学习能力',
      items: [
        '运用数字化工具辅助英语学习',
        '提高自主学习和合作学习能力',
        '培养数字化时代的学习素养'
      ]
    }
  ]
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // Title
  slide.addText(slideConfig.title, {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 28,
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
  
  // Objectives grid
  const boxWidth = 4.4;
  const boxHeight = 1.8;
  const gap = 0.3;
  
  slideConfig.objectives.forEach((obj, index) => {
    const row = Math.floor(index / 2);
    const col = index % 2;
    const x = 0.5 + (col * (boxWidth + gap));
    const y = 1.8 + (row * (boxHeight + gap));
    
    // Category box
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: boxWidth, h: boxHeight,
      fill: { color: index % 2 === 0 ? theme.light : "f8f9fa" },
      line: { color: theme.accent, width: 1 },
      rectRadius: 0.1
    });
    
    // Category title
    slide.addText(obj.category, {
      x: x + 0.2, y: y + 0.2, w: boxWidth - 0.4, h: 0.4,
      fontSize: 18,
      fontFace: "Microsoft YaHei",
      color: theme.primary,
      bold: true,
      valign: "middle"
    });
    
    // Items
    obj.items.forEach((item, itemIndex) => {
      const itemY = y + 0.7 + (itemIndex * 0.35);
      slide.addText(`• ${item}`, {
        x: x + 0.3, y: itemY, w: boxWidth - 0.6, h: 0.3,
        fontSize: 14,
        fontFace: "Microsoft YaHei",
        color: "333333",
        bullet: { type: 'bullet' }
      });
    });
  });
  
  // Page number badge
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("3", {
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
  pres.writeFile({ fileName: "slide-03-preview.pptx" });
}

module.exports = { createSlide, slideConfig };