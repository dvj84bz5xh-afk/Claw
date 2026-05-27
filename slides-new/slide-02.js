const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'toc',
  index: 2,
  title: '课件结构概览',
  items: [
    { title: '课程背景与理念', page: 3 },
    { title: '单元目标与核心素养', page: 4 },
    { title: '课时教学设计 (1-4)', page: 5 },
    { title: '技术融合应用', page: 9 },
    { title: '评价与反馈机制', page: 10 },
    { title: '教学反思与展望', page: 11 },
    { title: '专家评价与共识', page: 12 }
  ]
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };
  
  // 标题
  slide.addText(slideConfig.title, {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 36, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 装饰线
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.4, w: 9, h: 0,
    line: { color: theme.secondary, width: 2, dashType: "dash" }
  });
  
  // 目录项
  const startY = 1.8;
  const itemHeight = 0.6;
  
  slideConfig.items.forEach((item, index) => {
    const y = startY + index * itemHeight;
    
    // 编号圆点
    slide.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.15, w: 0.3, h: 0.3,
      fill: { color: theme.secondary }
    });
    
    slide.addText((index + 1).toString(), {
      x: 0.7, y: y + 0.15, w: 0.3, h: 0.3,
      fontSize: 14, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    // 标题
    slide.addText(item.title, {
      x: 1.2, y: y, w: 6, h: 0.5,
      fontSize: 22, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: false
    });
    
    // 页码
    slide.addText(item.page.toString(), {
      x: 7.5, y: y, w: 1, h: 0.5,
      fontSize: 20, fontFace: "Arial",
      color: theme.accent, bold: true,
      align: "right"
    });
    
    // 连接线
    if (index < slideConfig.items.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.85, y: y + 0.45, w: 0, h: itemHeight - 0.2,
        line: { color: theme.light, width: 1, dashType: "dot" }
      });
    }
  });
  
  // 底部说明
  slide.addText("共计 12 页，聚焦素养导向与单元整体教学", {
    x: 0.5, y: 5.0, w: 9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: theme.secondary, italic: true,
    align: "center"
  });
  
  // 页码标识
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fill: { color: theme.accent },
    rectRadius: 0.15
  });
  slide.addText("02", {
    x: 9.1, y: 5.15, w: 0.6, h: 0.35,
    fontSize: 11, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
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
  pres.writeFile({ fileName: "slide-02-preview.pptx" });
}

module.exports = { createSlide, slideConfig };