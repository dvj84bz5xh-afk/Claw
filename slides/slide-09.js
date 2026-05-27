// slides/slide-09.js
// Technology Application - Evaluation & Detection Assistant

const slideConfig = {
  title: "技术应用展示：评价检测助手",
  subtitle: "实现“教—学—评”即时循环",
  pageNumber: 9,
  content: {
    left: {
      title: "🔍 核心功能",
      items: [
        "课堂实时反馈：推送选择题、填空题至学生平板，自动统计正答率",
        "口语智能评价：从发音准确度、流利度、完整度三个维度给出评分与建议",
        "过程性数据可视化：生成知识点掌握热力图，便于教师动态调整教学"
      ]
    },
    right: {
      title: "💡 应用场景示例",
      sections: [
        {
          title: "场景一：当堂检测，即时反馈",
          text: "• 教师推送5道关于课程词汇的选择题\n• 系统30秒内收集全班答案，显示每题正确率\n• 针对错误率高的题目，教师即刻进行补充讲解"
        },
        {
          title: "场景二：口语练习，个性指导",
          text: "• 学生跟读句子“My favourite subject is art.”\n• 系统分析发音，标注问题音素，给出改进建议\n• 学生可反复练习，查看进步曲线"
        },
        {
          title: "场景三：学情分析，精准施策",
          text: "• 单元结束后，系统生成班级整体掌握情况报告\n• 识别薄弱环节（如“because句型运用”）\n• 教师据此设计针对性复习活动"
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
  
  // Visual element: Bar chart (simplified)
  const barData = [
    { label: "词汇", value: 85, color: theme.primary },
    { label: "句型", value: 72, color: theme.secondary },
    { label: "口语", value: 65, color: theme.accent }
  ];
  
  const chartX = 1.5, chartY = 5.5, barWidth = 0.8, barSpacing = 1.2;
  barData.forEach((item, i) => {
    const barHeight = item.value / 100 * 1.5;
    slide.addShape(pres.ShapeType.rect, {
      x: chartX + i * barSpacing,
      y: chartY + (1.5 - barHeight),
      w: barWidth,
      h: barHeight,
      fill: { color: item.color },
      line: { color: item.color }
    });
    slide.addText(item.label, {
      x: chartX + i * barSpacing,
      y: chartY + 1.6,
      w: barWidth,
      h: 0.3,
      fontSize: 12,
      align: 'center',
      fontFace: 'Microsoft YaHei'
    });
    slide.addText(`${item.value}%`, {
      x: chartX + i * barSpacing,
      y: chartY + (1.5 - barHeight) - 0.3,
      w: barWidth,
      h: 0.3,
      fontSize: 10,
      align: 'center',
      fontFace: 'Microsoft YaHei'
    });
  });
  
  slide.addText("知识点掌握情况", {
    x: chartX, y: chartY - 0.5, w: 4, h: 0.4,
    fontSize: 14, bold: true, align: 'center',
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