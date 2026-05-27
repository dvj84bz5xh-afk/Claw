// slides/slide-07.js
// Teaching Activity - Transfer & Innovation (Comprehensive Application)

const slideConfig = {
  title: "教学活动设计：综合运用",
  subtitle: "课时4：项目式学习“设计完美校园日”",
  pageNumber: 7,
  content: {
    left: {
      title: "🎯 项目任务",
      items: [
        "以小组为单位，设计一份“完美校园日（Perfect School Day）”方案",
        "方案需包括：课程安排、活动设计、理由阐述",
        "最终成果形式：海报、短视频或PPT演示"
      ]
    },
    right: {
      title: "📝 项目实施流程",
      sections: [
        {
          title: "阶段一：规划与分工 (10分钟)",
          text: "• 小组讨论确定主题（如：快乐运动日、艺术创意日）\n• 角色分工：组长、记录员、设计师、发言人\n• 使用项目计划模板明确任务与时间节点"
        },
        {
          title: "阶段二：设计与创作 (25分钟)",
          text: "• 绘制课程表与活动安排，可手绘或使用数字工具\n• 撰写英文介绍文案，运用本单元所学词汇句型\n• 制作成果（海报/视频），注重创意与视觉表达"
        },
        {
          title: "阶段三：展示与评价 (15分钟)",
          text: "• 小组代表展示成果，限时3分钟\n• 听众使用评价表从“语言、内容、合作、创意”评分\n• 教师点评，颁发“最佳设计”、“最佳合作”等虚拟奖项"
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
  
  // Left column: Task
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
  
  // Right column: Process
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
  
  // Visual element: Project timeline
  slide.addShape(pres.ShapeType.line, {
    x: 1, y: 5.5, w: 6, h: 0,
    line: { color: theme.secondary, width: 3 }
  });
  
  const milestones = [
    { x: 1, label: "规划", color: theme.primary },
    { x: 3, label: "设计", color: theme.secondary },
    { x: 5, label: "展示", color: theme.accent }
  ];
  
  milestones.forEach((milestone, i) => {
    slide.addShape(pres.ShapeType.roundRect, {
      x: milestone.x, y: 5.3, w: 1.2, h: 0.4,
      fill: { color: milestone.color },
      line: { color: milestone.color }
    });
    slide.addText(milestone.label, {
      x: milestone.x, y: 5.3, w: 1.2, h: 0.4,
      fontSize: 12, bold: true, color: 'FFFFFF',
      align: 'center', valign: 'middle',
      fontFace: 'Microsoft YaHei'
    });
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