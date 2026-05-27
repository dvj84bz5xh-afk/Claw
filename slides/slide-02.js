// slide-02.js - Table of Contents
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'toc',
  index: 2,
  title: '目录 Contents',
  sections: [
    '一、单元目标解读',
    '二、教学活动设计',
    '三、技术应用展示', 
    '四、专家评价建议',
    '五、实践总结展望'
  ]
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  
  // Title
  slide.addText(slideConfig.title, {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 32,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true,
    align: "center"
  });
  
  // Decorative line
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 1.4, w: 9, h: 0,
    line: { color: theme.secondary, width: 2 }
  });
  
  // Sections
  const startY = 1.8;
  const sectionHeight = 0.7;
  
  slideConfig.sections.forEach((section, index) => {
    const y = startY + (index * sectionHeight);
    
    // Section number
    slide.addText(`${index + 1}`, {
      x: 0.8, y: y + 0.1, w: 0.5, h: 0.5,
      fontSize: 24,
      fontFace: "Microsoft YaHei",
      color: theme.secondary,
      bold: true,
      align: "center",
      valign: "middle"
    });
    
    // Section text
    slide.addText(section, {
      x: 1.5, y: y, w: 7, h: 0.6,
      fontSize: 24,
      fontFace: "Microsoft YaHei",
      color: theme.primary,
      bold: true,
      valign: "middle"
    });
    
    // Connecting line
    slide.addShape(pres.shapes.LINE, {
      x: 1.4, y: y + 0.3, w: 0.1, h: 0,
      line: { color: theme.accent, width: 1, dashType: "dash" }
    });
  });
  
  // Visual element - timeline
  slide.addShape(pres.shapes.LINE, {
    x: 1, y: startY + 0.3, w: 0, h: (slideConfig.sections.length - 1) * sectionHeight,
    line: { color: theme.light, width: 4 },
    rotate: 0
  });
  
  // Page number badge (required for all slides except cover)
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("2", {
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
  pres.writeFile({ fileName: "slide-02-preview.pptx" });
}

module.exports = { createSlide, slideConfig };