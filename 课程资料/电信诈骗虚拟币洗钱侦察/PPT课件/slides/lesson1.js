const pptxgen = require("pptxgenjs");

// 主题配置 - 公安蓝配色
const theme = {
  primary: "1a365d",      // 深蓝 - 标题
  secondary: "2c5282",    // 中蓝 - 副标题
  accent: "3182ce",       // 亮蓝 - 强调
  light: "bee3f8",        // 浅蓝 - 背景
  bg: "f7fafc",           // 灰白 - 主背景
  danger: "c53030",       // 红色 - 警示
  success: "276749",      // 绿色
  warning: "c05621"       // 橙色
};

// 创建第一课时PPT
function createLesson1() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = '刑侦总队六支队';
  pres.company = '公安教育培训';
  pres.subject = '电信诈骗案中虚拟币洗钱侦察';
  
  // ===== 第1页：封面 =====
  const slide1 = pres.addSlide();
  slide1.background = { color: theme.primary };
  
  // 装饰条
  slide1.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.1,
    fill: { color: theme.accent }
  });
  
  // 课程标题
  slide1.addText("电信诈骗案中", {
    x: 0.5, y: 1.8, w: 9, h: 0.8,
    fontSize: 44, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true, align: "center"
  });
  
  slide1.addText("虚拟币洗钱侦察", {
    x: 0.5, y: 2.6, w: 9, h: 0.8,
    fontSize: 44, fontFace: "Microsoft YaHei",
    color: theme.accent, bold: true, align: "center"
  });
  
  // 副标题
  slide1.addText("第1课时：电信诈骗概述与虚拟币洗钱趋势", {
    x: 0.5, y: 3.6, w: 9, h: 0.5,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: "E2E8F0", align: "center"
  });
  
  // 底部信息
  slide1.addText("刑侦总队六支队", {
    x: 0.5, y: 4.8, w: 9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: "A0AEC0", align: "center"
  });
  
  slide1.addText("2026年4月", {
    x: 0.5, y: 5.1, w: 9, h: 0.3,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: "718096", align: "center"
  });
  
  // ===== 第2页：目录 =====
  const slide2 = pres.addSlide();
  slide2.background = { color: theme.bg };
  
  // 标题
  slide2.addText("本课时内容", {
    x: 0.5, y: 0.5, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 目录项
  const tocItems = [
    { num: "01", title: "课程介绍", desc: "课程目标与安排" },
    { num: "02", title: "电信网络诈骗概述", desc: "十大高发类型解析" },
    { num: "03", title: "虚拟币洗钱趋势", desc: "犯罪手法与发展趋势" },
    { num: "04", title: "典型案例分析", desc: "真实案例剖析" }
  ];
  
  tocItems.forEach((item, index) => {
    const y = 1.4 + index * 1;
    
    // 序号圆形背景
    slide2.addShape(pres.shapes.OVAL, {
      x: 0.8, y: y, w: 0.6, h: 0.6,
      fill: { color: theme.accent }
    });
    
    slide2.addText(item.num, {
      x: 0.8, y: y, w: 0.6, h: 0.6,
      fontSize: 18, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    // 标题
    slide2.addText(item.title, {
      x: 1.7, y: y + 0.05, w: 7, h: 0.35,
      fontSize: 22, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    // 描述
    slide2.addText(item.desc, {
      x: 1.7, y: y + 0.4, w: 7, h: 0.3,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 页码
  slide2.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide2.addText("2", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第3页：课程介绍 =====
  const slide3 = pres.addSlide();
  slide3.background = { color: theme.bg };
  
  slide3.addText("课程介绍", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 课程信息卡片
  const infoCards = [
    { label: "课程名称", value: "电信诈骗案中虚拟币洗钱侦察" },
    { label: "授课对象", value: "侦查专业在职民警" },
    { label: "总课时", value: "4课时（每课时45-60分钟）" },
    { label: "授课形式", value: "理论讲授 + 案例分析 + 实操演练" }
  ];
  
  infoCards.forEach((card, index) => {
    const y = 1.2 + index * 0.9;
    
    slide3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9, h: 0.75,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.1
    });
    
    slide3.addText(card.label, {
      x: 0.7, y: y + 0.2, w: 2, h: 0.35,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.secondary, bold: true
    });
    
    slide3.addText(card.value, {
      x: 2.8, y: y + 0.2, w: 6.4, h: 0.35,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary
    });
  });
  
  // 页码
  slide3.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide3.addText("3", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第4页：教学目标 =====
  const slide4 = pres.addSlide();
  slide4.background = { color: theme.bg };
  
  slide4.addText("教学目标", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 三大目标
  const objectives = [
    { 
      title: "知识目标", 
      color: theme.accent,
      items: ["了解电信网络诈骗十大高发类型", "理解虚拟币洗钱趋势", "掌握犯罪手法特点"]
    },
    { 
      title: "技能目标", 
      color: theme.success,
      items: ["识别常见诈骗类型", "分析虚拟币洗钱流程", "初步判断案件性质"]
    },
    { 
      title: "态度目标", 
      color: theme.warning,
      items: ["树立打击犯罪信心", "培养科技侦查意识", "建立依法办案观念"]
    }
  ];
  
  objectives.forEach((obj, index) => {
    const x = 0.5 + index * 3.2;
    
    // 卡片背景
    slide4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 1.3, w: 2.9, h: 3.5,
      fill: { color: "FFFFFF" },
      line: { color: obj.color, width: 2 },
      rectRadius: 0.15
    });
    
    // 标题背景条
    slide4.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.3, w: 2.9, h: 0.6,
      fill: { color: obj.color }
    });
    
    slide4.addText(obj.title, {
      x: x, y: 1.4, w: 2.9, h: 0.4,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: "FFFFFF", bold: true, align: "center"
    });
    
    // 列表项
    obj.items.forEach((item, i) => {
      slide4.addText("• " + item, {
        x: x + 0.2, y: 2.1 + i * 0.6, w: 2.5, h: 0.5,
        fontSize: 14, fontFace: "Microsoft YaHei",
        color: theme.primary
      });
    });
  });
  
  // 页码
  slide4.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide4.addText("4", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第5页：电信网络诈骗现状 =====
  const slide5 = pres.addSlide();
  slide5.background = { color: theme.bg };
  
  slide5.addText("电信网络诈骗现状", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 统计数据
  const stats = [
    { num: "194.5亿+", label: "2024年损失金额", unit: "人民币" },
    { num: "87.4%", label: "受害人为普通群众", unit: "占比" },
    { num: "TOP 10", label: "诈骗类型占发案", unit: "近80%" },
    { num: "30%+", label: "虚拟币洗钱占比", unit: "增长趋势" }
  ];
  
  stats.forEach((stat, index) => {
    const x = 0.5 + (index % 2) * 4.8;
    const y = 1.4 + Math.floor(index / 2) * 2;
    
    slide5.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: 4.5, h: 1.7,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.1
    });
    
    slide5.addText(stat.num, {
      x: x, y: y + 0.2, w: 4.5, h: 0.6,
      fontSize: 36, fontFace: "Arial",
      color: theme.danger, bold: true, align: "center"
    });
    
    slide5.addText(stat.label, {
      x: x, y: y + 0.85, w: 4.5, h: 0.4,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary, align: "center"
    });
    
    slide5.addText(stat.unit, {
      x: x, y: y + 1.2, w: 4.5, h: 0.3,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: theme.secondary, align: "center"
    });
  });
  
  // 页码
  slide5.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide5.addText("5", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第6页：十大高发类型 =====
  const slide6 = pres.addSlide();
  slide6.background = { color: theme.bg };
  
  slide6.addText("十大高发诈骗类型", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 十大类型列表
  const fraudTypes = [
    { rank: "1", name: "刷单返利类", percent: "30%", desc: "发案量最大", color: "C53030" },
    { rank: "2", name: "虚假投资理财", percent: "18%", desc: "损失最大", color: "C53030" },
    { rank: "3", name: "虚假网络贷款", percent: "12%", desc: "急需资金人群", color: "DD6B20" },
    { rank: "4", name: "冒充电商客服", percent: "10%", desc: "网购人群", color: "DD6B20" },
    { rank: "5", name: "冒充公检法", percent: "8%", desc: "恐吓诈骗", color: "D69E2E" },
    { rank: "6", name: "虚假征信", percent: "6%", desc: "冒充金融机构", color: "D69E2E" },
    { rank: "7", name: "杀猪盘", percent: "5%", desc: "情感诈骗", color: "38A169" },
    { rank: "8", name: "冒充领导", percent: "4%", desc: "熟人诈骗", color: "38A169" },
    { rank: "9", name: "游戏交易", percent: "4%", desc: "青少年群体", color: "3182CE" },
    { rank: "10", name: "冒充军警", percent: "3%", desc: "信任诈骗", color: "3182CE" }
  ];
  
  fraudTypes.forEach((type, index) => {
    const x = 0.5 + (index % 2) * 4.8;
    const y = 1.2 + Math.floor(index / 2) * 0.75;
    
    slide6.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: 4.5, h: 0.65,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.05
    });
    
    // 排名
    slide6.addShape(pres.shapes.OVAL, {
      x: x + 0.1, y: y + 0.12, w: 0.4, h: 0.4,
      fill: { color: type.color }
    });
    slide6.addText(type.rank, {
      x: x + 0.1, y: y + 0.12, w: 0.4, h: 0.4,
      fontSize: 14, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    // 类型名称
    slide6.addText(type.name, {
      x: x + 0.6, y: y + 0.15, w: 1.8, h: 0.35,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    // 占比
    slide6.addText(type.percent, {
      x: x + 2.6, y: y + 0.15, w: 0.8, h: 0.35,
      fontSize: 14, fontFace: "Arial",
      color: type.color, bold: true
    });
    
    // 描述
    slide6.addText(type.desc, {
      x: x + 3.4, y: y + 0.18, w: 1, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 页码
  slide6.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide6.addText("6", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第7页：虚拟币洗钱概述 =====
  const slide7 = pres.addSlide();
  slide7.background = { color: theme.bg };
  
  slide7.addText("虚拟币洗钱概述", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 为什么犯罪集团选择虚拟币？
  slide7.addText("为什么犯罪集团选择虚拟币洗钱？", {
    x: 0.5, y: 1.2, w: 9, h: 0.4,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: theme.secondary, bold: true
  });
  
  const features = [
    { icon: "匿名性", title: "匿名性强", desc: "无需真实身份，地址无法直接关联" },
    { icon: "去中心化", title: "去中心化", desc: "无监管中介，难以冻结账户" },
    { icon: "跨境", title: "跨境便捷", desc: "资金秒级全球转移，无视国界" },
    { icon: "不可逆", title: "交易不可逆", desc: "转账后无法撤回，难以追回" },
    { icon: "混币", title: "混币服务", desc: "可切断资金链条，混淆来源" }
  ];
  
  features.forEach((feat, index) => {
    const y = 1.8 + index * 0.65;
    
    slide7.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9, h: 0.55,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.05
    });
    
    // 图标区域
    slide7.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y: y, w: 0.15, h: 0.55,
      fill: { color: theme.accent }
    });
    
    slide7.addText(feat.title, {
      x: 0.8, y: y + 0.1, w: 2, h: 0.35,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    slide7.addText(feat.desc, {
      x: 3, y: y + 0.13, w: 6, h: 0.3,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 页码
  slide7.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide7.addText("7", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第8页：虚拟币洗钱趋势 =====
  const slide8 = pres.addSlide();
  slide8.background = { color: theme.bg };
  
  slide8.addText("2024年虚拟币洗钱新趋势", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  const trends = [
    { 
      title: "DeFi协议洗钱增多", 
      desc: "利用去中心化金融协议进行资金清洗",
      tag: "新型",
      tagColor: "C53030"
    },
    { 
      title: "跨链桥转移资金", 
      desc: "通过跨链桥在不同公链间转移，增加追踪难度",
      tag: "热门",
      tagColor: "DD6B20"
    },
    { 
      title: "NFT用于洗白", 
      desc: "通过高价买卖NFT实现资金洗白",
      tag: "新型",
      tagColor: "C53030"
    },
    { 
      title: "稳定币USDT成主流", 
      desc: "避免价格波动风险，USDT成为首选",
      tag: "主流",
      tagColor: "3182CE"
    },
    { 
      title: "暗网交易活跃", 
      desc: "通过暗网进行非法交易和资金转移",
      tag: "隐蔽",
      tagColor: "805AD5"
    }
  ];
  
  trends.forEach((trend, index) => {
    const y = 1.3 + index * 0.75;
    
    slide8.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9, h: 0.65,
      fill: { color: "FFFFFF" },
      line: { color: theme.light, width: 1 },
      rectRadius: 0.08
    });
    
    // 标签
    slide8.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.7, y: y + 0.15, w: 0.8, h: 0.35,
      fill: { color: trend.tagColor },
      rectRadius: 0.1
    });
    slide8.addText(trend.tag, {
      x: 0.7, y: y + 0.18, w: 0.8, h: 0.3,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    slide8.addText(trend.title, {
      x: 1.7, y: y + 0.1, w: 3, h: 0.35,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true
    });
    
    slide8.addText(trend.desc, {
      x: 1.7, y: y + 0.42, w: 7.5, h: 0.25,
      fontSize: 12, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });
  
  // 页码
  slide8.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide8.addText("8", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第9页：典型案例 =====
  const slide9 = pres.addSlide();
  slide9.background = { color: theme.bg };
  
  slide9.addText("典型案例分析", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 案例卡片
  slide9.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.2, w: 9, h: 3.5,
    fill: { color: "FFFFFF" },
    line: { color: theme.accent, width: 2 },
    rectRadius: 0.15
  });
  
  // 案例标题
  slide9.addText("案例：某电信诈骗集团虚拟币洗钱案", {
    x: 0.7, y: 1.4, w: 8.6, h: 0.4,
    fontSize: 20, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 案例详情
  const caseDetails = [
    { label: "案件类型", value: "虚假投资理财 + 虚拟币洗钱" },
    { label: "涉案金额", value: "超过 8 亿元人民币" },
    { label: "受害人数", value: "全国十余个省市，3000余人" },
    { label: "洗钱方式", value: "USDT转账 → 混币器 → OTC场外交易" },
    { label: "犯罪特点", value: "境外操控、多层代理、技术隐蔽" }
  ];
  
  caseDetails.forEach((item, index) => {
    const y = 1.95 + index * 0.5;
    
    slide9.addText(item.label + ":", {
      x: 0.9, y: y, w: 2, h: 0.35,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.secondary, bold: true
    });
    
    slide9.addText(item.value, {
      x: 2.8, y: y, w: 6.4, h: 0.35,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.primary
    });
  });
  
  // 侦查启示
  slide9.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.1, w: 8.6, h: 0.5,
    fill: { color: theme.light }
  });
  slide9.addText("侦查启示：关注资金流向 + 掌握链上追踪技术 + 加强跨境协作", {
    x: 0.9, y: 4.2, w: 8.2, h: 0.3,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: theme.primary
  });
  
  // 页码
  slide9.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide9.addText("9", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第10页：本课小结 =====
  const slide10 = pres.addSlide();
  slide10.background = { color: theme.bg };
  
  slide10.addText("本课小结", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 小结要点
  const summaryPoints = [
    "电信网络诈骗十大高发类型：刷单返利、虚假投资等占比近80%",
    "虚拟币洗钱优势：匿名性、去中心化、跨境便捷、交易不可逆",
    "2024年新趋势：DeFi协议、跨链桥、NFT洗白、USDT主流化",
    "侦查重点：资金流向分析、链上追踪技术、跨境协作机制"
  ];
  
  summaryPoints.forEach((point, index) => {
    const y = 1.3 + index * 0.9;
    
    slide10.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.1, w: 0.35, h: 0.35,
      fill: { color: theme.accent }
    });
    slide10.addText((index + 1).toString(), {
      x: 0.7, y: y + 0.1, w: 0.35, h: 0.35,
      fontSize: 14, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });
    
    slide10.addText(point, {
      x: 1.3, y: y, w: 8, h: 0.7,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.primary
    });
  });
  
  // 页码
  slide10.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide10.addText("10", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第11页：课后作业 =====
  const slide11 = pres.addSlide();
  slide11.background = { color: theme.bg };
  
  slide11.addText("课后作业", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });
  
  // 作业内容
  slide11.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 1.2, w: 9, h: 3.5,
    fill: { color: "FFFFFF" },
    line: { color: theme.accent, width: 2 },
    rectRadius: 0.15
  });
  
  slide11.addText("作业内容", {
    x: 0.7, y: 1.4, w: 8.6, h: 0.4,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: theme.accent, bold: true
  });
  
  const homeworkItems = [
    "1. 查阅资料，了解比特币（BTC）或以太坊（ETH）的基本原理",
    "2. 访问欧科云链（OKLink）或 Etherscan 网站",
    "3. 熟悉区块链浏览器界面，了解交易查询功能",
    "4. 思考：为什么虚拟币会被用于洗钱？列举3个原因"
  ];
  
  homeworkItems.forEach((item, index) => {
    slide11.addText(item, {
      x: 0.9, y: 2 + index * 0.55, w: 8.4, h: 0.5,
      fontSize: 15, fontFace: "Microsoft YaHei",
      color: theme.primary
    });
  });
  
  // 提交要求
  slide11.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.3, w: 8.6, h: 0.6,
    fill: { color: theme.light }
  });
  slide11.addText("提交要求：下次课前提交学习笔记，记录查询过程和心得体会", {
    x: 0.9, y: 4.45, w: 8.2, h: 0.3,
    fontSize: 13, fontFace: "Microsoft YaHei",
    color: theme.secondary
  });
  
  // 页码
  slide11.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide11.addText("11", {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
  
  // ===== 第12页：结束页 =====
  const slide12 = pres.addSlide();
  slide12.background = { color: theme.primary };
  
  // 装饰条
  slide12.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.1,
    fill: { color: theme.accent }
  });
  
  slide12.addText("感谢聆听", {
    x: 0.5, y: 2.2, w: 9, h: 0.8,
    fontSize: 48, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true, align: "center"
  });
  
  slide12.addText("下节课预告：区块链技术基础与虚拟币原理", {
    x: 0.5, y: 3.2, w: 9, h: 0.5,
    fontSize: 18, fontFace: "Microsoft YaHei",
    color: theme.accent, align: "center"
  });
  
  slide12.addText("刑侦总队六支队", {
    x: 0.5, y: 4.5, w: 9, h: 0.4,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: "A0AEC0", align: "center"
  });
  
  // 保存文件
  pres.writeFile({ fileName: "C:\\Users\\10127\\WorkBuddy\\Claw\\课程资料\\电信诈骗虚拟币洗钱侦察\\PPT课件\\第1课时-电信诈骗概述与虚拟币洗钱趋势.pptx" });
  
  console.log("第1课时PPT已生成：第1课时-电信诈骗概述与虚拟币洗钱趋势.pptx");
}

// 执行生成
createLesson1();
