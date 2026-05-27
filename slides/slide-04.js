// slide-04.js - Teaching Activity - Scenario Introduction
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 4,
  title: '二、教学活动设计 - 情境导入',
  activity: '情境创设：五育少年Peter获奖采访',
  time: '时间：5分钟',
  objectives: [
    '创设真实情境，激发学习兴趣',
    '引出核心任务：采访Peter的一周活动',
    '激活已有知识，建立新旧联系'
  ],
  steps: [
    '播放Peter获奖短视频',
    '提出问题：What does Peter do in a week?',
    '明确采访任务要求',
    '分组讨论初步预测'
  ],
  tech: '技术应用：教学助手推送情境视频'
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
  
  // Activity highlight
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.3, w: 9, h: 0.8,
    fill: { color: theme.light },
    line: { color: theme.secondary, width: 2 },
    rectRadius: 0.1
  });
  
  slide.addText(slideConfig.activity, {
    x: 0.7, y: 1.5, w: 8.6, h: 0.4,
    fontSize: 20,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true,
    align: "center",
    valign: "middle"
  });
  
  // Time indicator
  slide.addText(slideConfig.time, {
    x: 0.5, y: 2.2, w: 9, h: 0.4,
    fontSize: 16,
    fontFace: "Microsoft YaHei",
    color: theme.secondary,
    align: "center"
  });
  
  // Left column - Objectives
  slide.addText('教学目标', {
    x: 0.5, y: 2.7, w: 4, h: 0.4,
    fontSize: 18,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true
  });
  
  slideConfig.objectives.forEach((obj, index) => {
    slide.addText(`${index + 1}. ${obj}`, {
      x: 0.7, y: 3.2 + (index * 0.35), w: 3.8, h: 0.3,
      fontSize: 14,
      fontFace: "Microsoft YaHei",
      color: "333333"
    });
  });
  
  // Right column - Steps
  slide.addText('活动步骤', {
    x: 5, y: 2.7, w: 4, h: 0.4,
    fontSize: 18,
    fontFace: "Microsoft YaHei",
    color: theme.primary,
    bold: true
  });
  
  slideConfig.steps.forEach((step, index) => {
    slide.addText(`${index + 1}. ${step}`, {
      x: 5.2, y: 3.2 + (index * 0.35), w: 3.8, h: 0.3,
      fontSize: 14,
      fontFace: "Microsoft YaHei",
      color: "333333"
    });
  });
  
  // Technology application
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.7, w: 9, h: 0.5,
    fill: { color: theme.accent, transparency: 20 },
    line: { color: theme.accent, width: 1 }
  });
  
  slide.addText(slideConfig.tech, {
    x: 0.7, y: 4.8, w: 8.6, h: 0.3,
    fontSize: 16,
    fontFace: "Microsoft YaHei",
    color: theme.secondary,
    bold: true,
    align: "center",
    valign: "middle"
  });
  
  // Page number badge
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText("4", {
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
  pres.writeFile({ fileName: "slide-04-preview.pptx" });
}

module.exports = { createSlide, slideConfig };