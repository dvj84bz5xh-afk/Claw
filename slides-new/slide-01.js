const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: '素养导向下的小学英语单元整体教学设计',
  subtitle: '以四年级下册 Module 3 Unit 3 "Days of the week"为例',
  author: '上海市徐汇区教育学院',
  date: '2026年4月'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };
  
  // 主标题
  slide.addText(slideConfig.title, {
    x: 0.5, y: 1.5, w: 9, h: 1.5,
    fontSize: 40, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true, align: "center",
    shadow: { type: "outer", color: "000000", blur: 15, offset: 3 }
  });
  
  // 副标题
  slide.addText(slideConfig.subtitle, {
    x: 0.5, y: 3.2, w: 9, h: 0.8,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: "FFFFFF", align: "center", italic: true
  });
  
  // 装饰线
  slide.addShape(pres.shapes.LINE, {
    x: 2, y: 4.1, w: 6, h: 0,
    line: { color: theme.light, width: 2 }
  });
  
  // 单位信息
  slide.addText("主办单位", {
    x: 2, y: 4.5, w: 6, h: 0.5,
    fontSize: 18, fontFace: "Arial",
    color: "FFFFFF", align: "center", bold: true
  });
  
  slide.addText(slideConfig.author, {
    x: 2, y: 5.0, w: 6, h: 0.6,
    fontSize: 22, fontFace: "Microsoft YaHei",
    color: "FFFFFF", align: "center"
  });
  
  // 日期
  slide.addText(slideConfig.date, {
    x: 2, y: 5.8, w: 6, h: 0.5,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: theme.light, align: "center"
  });
  
  // 底部装饰元素
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 5.2, w: 9, h: 0.3,
    fill: { color: "FFFFFF", transparency: 20 },
    rectRadius: 0.1
  });
  
  return slide;
}

// 独立预览功能
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
  pres.writeFile({ fileName: "slide-01-preview.pptx" });
}

module.exports = { createSlide, slideConfig };