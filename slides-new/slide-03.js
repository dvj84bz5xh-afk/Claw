const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 3,
  title: '课程背景与理念',
  subtitle: '基于《义务教育英语课程标准（2025修订版）》',
  sections: [
    {
      title: '政策背景',
      content: '• 2025修订版强调"文明交流互鉴"与"教育优质均衡发展"\n• 强化中华文化立场，注重跨文化沟通中传播中华文化\n• 聚焦核心素养落地，推动学习方式变革'
    },
    {
      title: '教学理念',
      content: '• 素养导向：语言能力、文化意识、思维品质、学习能力协同发展\n• 单元整体：以"大观念"统整教学内容，打破课时碎片化\n• 学生中心：从"教师讲授"转向"学生探究"，强化自主学习\n• 技术赋能：信息技术与英语教学深度融合，促进个性化学习'
    },
    {
      title: '上海特色',
      content: '• 单元整体教学实践自2008年持续深化，形成完整教研体系\n• "语境带动、语用体验"成为核心教学策略\n• 数字化转型走在前列，"三个助手"平台应用广泛'
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
  
  // 装饰线
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.9, w: 9, h: 0,
    line: { color: theme.light, width: 1 }
  });
  
  // 三栏布局
  const columnWidth = 2.8;
  const startX = 0.5;
  const columnGap = 0.5;
  
  slideConfig.sections.forEach((section, index) => {
    const x = startX + index * (columnWidth + columnGap);
    
    // 卡片背景
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 2.2, w: columnWidth, h: 2.8,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.15
    });
    
    // 标题背景色块
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 2.2, w: columnWidth, h: 0.5,
      fill: { color: index === 0 ? theme.primary : index === 1 ? theme.secondary : theme.accent },
      rectRadius: 0.15
    });
    
    // 标题
    slide.addText(section.title, {
      x: x + 0.2, y: 2.25, w: columnWidth - 0.4, h: 0.4,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    // 内容
    slide.addText(section.content, {
      x: x + 0.2, y: 2.8, w: columnWidth - 0.4, h: 2.0,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.primary,
      lineSpacing: 1.2
    });
  });
  
  // 底部说明
  slide.addText("核心素养导向已成为英语教学改革的关键方向", {
    x: 0.5, y: 5.1, w: 9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: theme.secondary,
    align: "center"
  });
  
  // 页码标识
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fill: { color: theme.accent },
    rectRadius: 0.15
  });
  slide.addText("03", {
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
  pres.writeFile({ fileName: "slide-03-preview.pptx" });
}

module.exports = { createSlide, slideConfig };