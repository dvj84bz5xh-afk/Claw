const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 4,
  title: '单元目标与核心素养分解',
  subtitle: '四年级下册 Module 3 Unit 3 "Days of the week"',
  competencies: [
    {
      name: '语言能力',
      icon: '💬',
      goals: [
        '掌握一周七天的英文表达及相关词汇',
        '学会使用频度副词描述日常活动',
        '能听懂、会说核心句型：On Monday, Peter plays basketball.'
      ]
    },
    {
      name: '文化意识',
      icon: '🌍',
      goals: [
        '理解中西方时间管理观念的差异',
        '认同健康生活习惯的重要性',
        '培养守时意识和时间规划能力'
      ]
    },
    {
      name: '思维品质',
      icon: '🧠',
      goals: [
        '通过对比分析频度副词的差异',
        '发展信息筛选和逻辑表达能力',
        '在任务驱动下培养创造性思维'
      ]
    },
    {
      name: '学习能力',
      icon: '📚',
      goals: [
        '运用数字化工具辅助英语学习',
        '提高自主学习和合作学习能力',
        '培养数字化时代的学习素养'
      ]
    }
  ]
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };
  
  // 主标题
  slide.addText(slideConfig.title, {
    x: 0.5, y: 0.5, w: 9, h: 0.7,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 副标题
  slide.addText(slideConfig.subtitle, {
    x: 0.5, y: 1.3, w: 9, h: 0.5,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: theme.secondary, italic: true
  });
  
  // 四象限布局
  const quadrantSize = 4.2;
  const startX = 0.5;
  const startY = 2.0;
  
  slideConfig.competencies.forEach((comp, index) => {
    const row = Math.floor(index / 2);
    const col = index % 2;
    const x = startX + col * (quadrantSize + 0.5);
    const y = startY + row * (quadrantSize + 0.3);
    
    // 能力卡片
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: quadrantSize, h: quadrantSize,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.2
    });
    
    // 标题区域
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: quadrantSize, h: 0.8,
      fill: { color: theme.primary },
      rectRadius: 0.2
    });
    
    // 图标和标题
    slide.addText(comp.icon + " " + comp.name, {
      x: x + 0.3, y: y + 0.15, w: quadrantSize - 0.6, h: 0.5,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: "FFFFFF", bold: true,
      align: "left", valign: "middle"
    });
    
    // 目标列表
    const goalStartY = y + 1.0;
    comp.goals.forEach((goal, goalIndex) => {
      const goalY = goalStartY + goalIndex * 0.5;
      
      // 列表符号
      slide.addShape(pres.shapes.OVAL, {
        x: x + 0.3, y: goalY + 0.1, w: 0.2, h: 0.2,
        fill: { color: theme.secondary }
      });
      
      // 目标文本
      slide.addText(goal, {
        x: x + 0.6, y: goalY, w: quadrantSize - 0.8, h: 0.4,
        fontSize: 13, fontFace: "Microsoft YaHei",
        color: theme.primary,
        lineSpacing: 1.1
      });
    });
  });
  
  // 页码标识
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fill: { color: theme.accent },
    rectRadius: 0.15
  });
  slide.addText("04", {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fontSize: 11, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  return slide;
}

if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "2ec4b6",
    secondary: "ff9f1c",
    accent: "e71d36",
    light: "ffbf69",
    bg: "f2f2f2"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "slide-04-preview.pptx" });
}

module.exports = { createSlide, slideConfig };