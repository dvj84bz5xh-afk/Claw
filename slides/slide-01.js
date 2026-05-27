// slide-01.js - Cover Page
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: '素养导向下基于"三个助手"平台的单元整体教学实践',
  subtitle: '小学英语单元整体教学课件',
  school: '上海大学附属学校',
  teacher: '授课教师：严俊怡',
  date: '2024年5月'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // Background with color accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.5,
    fill: { color: theme.secondary }
  });
  
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.625 - 1, w: 10, h: 1,
    fill: { color: theme.primary }
  });
  
  // Main title
  slide.addText(slideConfig.title, {
    x: 0.5, y: 1.8, w: 9, h: 1.8,
    fontSize: 32,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true,
    align: "center",
    valign: "middle",
    lineSpacing: 1.5
  });
  
  // Subtitle
  slide.addText(slideConfig.subtitle, {
    x: 0.5, y: 3.8, w: 9, h: 0.6,
    fontSize: 24,
    fontFace: "Microsoft YaHei",
    color: theme.secondary,
    bold: true,
    align: "center"
  });
  
  // School name
  slide.addText(slideConfig.school, {
    x: 0.5, y: 4.6, w: 9, h: 0.5,
    fontSize: 28,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true,
    align: "center"
  });
  
  // Teacher info
  slide.addText(slideConfig.teacher, {
    x: 0.5, y: 5.2, w: 9, h: 0.4,
    fontSize: 20,
    fontFace: "Microsoft YaHei",
    color: "000000",
    align: "center"
  });
  
  // Date
  slide.addText(slideConfig.date, {
    x: 0.5, y: 5.6, w: 9, h: 0.4,
    fontSize: 18,
    fontFace: "Microsoft YaHei",
    color: "666666",
    align: "center"
  });
  
  // Decorative elements
  slide.addShape(pres.shapes.OVAL, {
    x: 2, y: 1, w: 0.8, h: 0.8,
    fill: { color: theme.light, transparency: 30 }
  });
  
  slide.addShape(pres.shapes.OVAL, {
    x: 7.5, y: 1.2, w: 0.5, h: 0.5,
    fill: { color: theme.accent, transparency: 40 }
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
  pres.writeFile({ fileName: "slide-01-preview.pptx" });
}

module.exports = { createSlide, slideConfig };