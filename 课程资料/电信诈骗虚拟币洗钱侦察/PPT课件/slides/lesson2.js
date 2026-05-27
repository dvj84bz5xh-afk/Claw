const pptxgen = require("pptxgenjs");

const theme = {
  primary: "1a365d",
  secondary: "2c5282",
  accent: "3182ce",
  light: "bee3f8",
  bg: "f7fafc",
  danger: "c53030",
  success: "276749",
  warning: "c05621"
};

function createLesson2() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = '刑侦总队六支队';
  
  // 封面
  const slide1 = pres.addSlide();
  slide1.background = { color: theme.primary };
  slide1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  slide1.addText("区块链技术基础", { x: 0.5, y: 1.8, w: 9, h: 0.8, fontSize: 44, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  slide1.addText("与虚拟币原理", { x: 0.5, y: 2.6, w: 9, h: 0.8, fontSize: 44, fontFace: "Microsoft YaHei", color: theme.accent, bold: true, align: "center" });
  slide1.addText("第2课时", { x: 0.5, y: 3.6, w: 9, h: 0.5, fontSize: 20, fontFace: "Microsoft YaHei", color: "E2E8F0", align: "center" });
  slide1.addText("刑侦总队六支队", { x: 0.5, y: 4.8, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  // 目录
  const slide2 = pres.addSlide();
  slide2.background = { color: theme.bg };
  slide2.addText("本课时内容", { x: 0.5, y: 0.5, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const toc = [
    { num: "01", title: "区块链技术原理", desc: "分布式账本与共识机制" },
    { num: "02", title: "主流虚拟币种", desc: "BTC、ETH、USDT特性对比" },
    { num: "03", title: "钱包与地址体系", desc: "公私钥与地址生成" },
    { num: "04", title: "交易机制解析", desc: "转账原理与Gas费" }
  ];
  toc.forEach((item, i) => {
    const y = 1.4 + i * 1;
    slide2.addShape(pres.shapes.OVAL, { x: 0.8, y: y, w: 0.6, h: 0.6, fill: { color: theme.accent }});
    slide2.addText(item.num, { x: 0.8, y: y, w: 0.6, h: 0.6, fontSize: 18, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
    slide2.addText(item.title, { x: 1.7, y: y + 0.05, w: 7, h: 0.35, fontSize: 22, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
    slide2.addText(item.desc, { x: 1.7, y: y + 0.4, w: 7, h: 0.3, fontSize: 14, fontFace: "Microsoft YaHei", color: theme.secondary });
  });
  slide2.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide2.addText("2", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 区块链定义
  const slide3 = pres.addSlide();
  slide3.background = { color: theme.bg };
  slide3.addText("什么是区块链？", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  slide3.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 9, h: 1.5, fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 2 }, rectRadius: 0.15 });
  slide3.addText("区块链是一种分布式账本技术，通过密码学原理将数据区块按时间顺序相连，形成不可篡改的链式结构。", { x: 0.8, y: 1.6, w: 8.4, h: 0.9, fontSize: 18, fontFace: "Microsoft YaHei", color: theme.primary });
  
  const features = [
    { title: "去中心化", desc: "无单一控制节点，数据分布式存储" },
    { title: "不可篡改", desc: "修改需控制51%节点，几乎不可能" },
    { title: "透明可追溯", desc: "所有交易公开可查，永久记录" },
    { title: "智能合约", desc: "自动执行的代码合约，无需中介" }
  ];
  features.forEach((f, i) => {
    const x = 0.5 + (i % 2) * 4.8;
    const y = 3.1 + Math.floor(i / 2) * 1;
    slide3.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x, y: y, w: 4.5, h: 0.9, fill: { color: "FFFFFF" }, line: { color: theme.light, width: 1 }, rectRadius: 0.1 });
    slide3.addText(f.title, { x: x + 0.2, y: y + 0.15, w: 4.1, h: 0.35, fontSize: 16, fontFace: "Microsoft YaHei", color: theme.accent, bold: true });
    slide3.addText(f.desc, { x: x + 0.2, y: y + 0.5, w: 4.1, h: 0.35, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary });
  });
  slide3.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide3.addText("3", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 区块结构
  const slide4 = pres.addSlide();
  slide4.background = { color: theme.bg };
  slide4.addText("区块结构", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  // 区块图示
  slide4.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.5, w: 4, h: 3.5, fill: { color: theme.primary }, rectRadius: 0.15 });
  slide4.addText("区块头", { x: 0.7, y: 1.7, w: 3.6, h: 0.4, fontSize: 18, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true });
  const headers = ["• 前一区块哈希", "• 时间戳", "• Merkle根", "• 随机数（Nonce）"];
  headers.forEach((h, i) => {
    slide4.addText(h, { x: 0.9, y: 2.2 + i * 0.45, w: 3.4, h: 0.4, fontSize: 14, fontFace: "Microsoft YaHei", color: "E2E8F0" });
  });
  slide4.addText("区块体", { x: 0.7, y: 4.2, w: 3.6, h: 0.4, fontSize: 18, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true });
  slide4.addText("• 交易数据列表", { x: 0.9, y: 4.7, w: 3.4, h: 0.4, fontSize: 14, fontFace: "Microsoft YaHei", color: "E2E8F0" });
  
  // 链式结构
  slide4.addShape(pres.shapes.RECTANGLE, { x: 5, y: 2.5, w: 1, h: 0.3, fill: { color: theme.accent }});
  slide4.addShape(pres.shapes.RECTANGLE, { x: 6.2, y: 2.5, w: 1, h: 0.3, fill: { color: theme.accent }});
  slide4.addShape(pres.shapes.RECTANGLE, { x: 7.4, y: 2.5, w: 1, h: 0.3, fill: { color: theme.accent }});
  slide4.addText("区块1 → 区块2 → 区块3", { x: 5, y: 3, w: 3.4, h: 0.4, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary, align: "center" });
  slide4.addText("每个区块包含前一区块的哈希，\n形成链式结构，确保数据不可篡改", { x: 5, y: 3.8, w: 4.5, h: 0.8, fontSize: 13, fontFace: "Microsoft YaHei", color: theme.primary });
  
  slide4.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide4.addText("4", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 主流币种
  const slide5 = pres.addSlide();
  slide5.background = { color: theme.bg };
  slide5.addText("主流虚拟币种对比", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  const coins = [
    { name: "BTC", full: "比特币", color: "F7931A", features: "加密货币鼻祖", use: "价值存储、大额转移" },
    { name: "ETH", full: "以太坊", color: "627EEA", features: "智能合约平台", use: "DeFi、代币发行" },
    { name: "USDT", full: "泰达币", color: "26A17B", features: "美元稳定币", use: "价值稳定、流通媒介" },
    { name: "XMR", full: "门罗币", color: "FF6600", features: "完全匿名", use: "隐私保护、终极洗白" }
  ];
  
  coins.forEach((coin, i) => {
    const y = 1.3 + i * 0.95;
    slide5.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: y, w: 9, h: 0.85, fill: { color: "FFFFFF" }, line: { color: theme.light, width: 1 }, rectRadius: 0.1 });
    slide5.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: y + 0.15, w: 1.2, h: 0.55, fill: { color: coin.color }, rectRadius: 0.1 });
    slide5.addText(coin.name, { x: 0.6, y: y + 0.22, w: 1.2, h: 0.4, fontSize: 18, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
    slide5.addText(coin.full, { x: 2, y: y + 0.1, w: 1.5, h: 0.35, fontSize: 16, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
    slide5.addText("特性：" + coin.features, { x: 3.7, y: y + 0.1, w: 3, h: 0.3, fontSize: 13, fontFace: "Microsoft YaHei", color: theme.secondary });
    slide5.addText("洗钱用途：" + coin.use, { x: 3.7, y: y + 0.45, w: 5, h: 0.3, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.danger });
  });
  
  slide5.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide5.addText("5", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // USDT重点
  const slide6 = pres.addSlide();
  slide6.background = { color: theme.bg };
  slide6.addText("稳定币 USDT：洗钱者的首选", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  slide6.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 9, h: 3.8, fill: { color: "FFFFFF" }, line: { color: "26A17B", width: 3 }, rectRadius: 0.15 });
  
  slide6.addText("USDT（泰达币）是与美元1:1锚定的稳定币", { x: 0.8, y: 1.6, w: 8.4, h: 0.4, fontSize: 18, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  const usdtPoints = [
    "✓ 价格稳定：避免BTC等币种的价格波动风险",
    "✓ 流通广泛：全球各大交易所均支持",
    "✓ 转账快速：链上转账几分钟到账",
    "✓ 隐蔽性强：无需银行账户，匿名转账",
    "✓ 变现容易：通过OTC场外交易快速兑换法币"
  ];
  usdtPoints.forEach((p, i) => {
    slide6.addText(p, { x: 0.9, y: 2.2 + i * 0.55, w: 8.4, h: 0.5, fontSize: 15, fontFace: "Microsoft YaHei", color: theme.secondary });
  });
  
  slide6.addShape(pres.shapes.RECTANGLE, { x: 0.8, y: 4.6, w: 8.4, h: 0.5, fill: { color: theme.light }});
  slide6.addText("侦查提示：USDT交易占比超过70%，是虚拟币洗钱的主要载体", { x: 1, y: 4.7, w: 8, h: 0.3, fontSize: 13, fontFace: "Microsoft YaHei", color: theme.primary });
  
  slide6.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide6.addText("6", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 钱包体系
  const slide7 = pres.addSlide();
  slide7.background = { color: theme.bg };
  slide7.addText("钱包与地址体系", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  // 公私钥图示
  slide7.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.3, w: 4.3, h: 3.8, fill: { color: theme.primary }, rectRadius: 0.15 });
  slide7.addText("私钥（Private Key）", { x: 0.7, y: 1.5, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true });
  slide7.addText("• 随机生成的大数字\n• 只有持有者知道\n• 用于签名交易\n• 丢失即丢失资产", { x: 0.9, y: 2.1, w: 3.5, h: 1.8, fontSize: 13, fontFace: "Microsoft YaHei", color: "E2E8F0" });
  slide7.addText("公钥（Public Key）", { x: 0.7, y: 3.6, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true });
  slide7.addText("• 由私钥推导而来\n• 可公开分享\n• 用于验证签名", { x: 0.9, y: 4.1, w: 3.5, h: 1.2, fontSize: 13, fontFace: "Microsoft YaHei", color: "E2E8F0" });
  
  // 地址生成
  slide7.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.2, y: 1.3, w: 4.3, h: 3.8, fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 2 }, rectRadius: 0.15 });
  slide7.addText("钱包地址", { x: 5.4, y: 1.5, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  slide7.addText("由公钥经过哈希运算生成\n是一串字母数字组合\n用于接收和发送虚拟币", { x: 5.6, y: 2.1, w: 3.5, h: 1.2, fontSize: 13, fontFace: "Microsoft YaHei", color: theme.secondary });
  slide7.addText("示例：", { x: 5.4, y: 3.4, w: 3.9, h: 0.3, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary });
  slide7.addShape(pres.shapes.RECTANGLE, { x: 5.6, y: 3.8, w: 3.7, h: 0.8, fill: { color: theme.light }});
  slide7.addText("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", { x: 5.7, y: 4, w: 3.5, h: 0.4, fontSize: 10, fontFace: "Courier New", color: theme.primary });
  slide7.addText("地址可公开，但无法从地址反推私钥", { x: 5.4, y: 4.8, w: 3.9, h: 0.3, fontSize: 11, fontFace: "Microsoft YaHei", color: theme.danger });
  
  slide7.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide7.addText("7", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 钱包类型
  const slide8 = pres.addSlide();
  slide8.background = { color: theme.bg };
  slide8.addText("钱包类型对比", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  const wallets = [
    { type: "热钱包", color: "DD6B20", pros: "使用方便、随时访问", cons: "联网风险、易被盗", users: "日常小额、频繁交易" },
    { type: "冷钱包", color: "3182CE", pros: "离线存储、安全性高", cons: "使用不便、需物理保管", users: "大额存储、长期持有" },
    { type: "硬件钱包", color: "805AD5", pros: "物理隔离、专业安全", cons: "价格较高、操作复杂", users: "专业用户、机构" }
  ];
  
  wallets.forEach((w, i) => {
    const x = 0.5 + i * 3.1;
    slide8.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x, y: 1.3, w: 2.9, h: 3.8, fill: { color: "FFFFFF" }, line: { color: w.color, width: 2 }, rectRadius: 0.15 });
    slide8.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.3, w: 2.9, h: 0.6, fill: { color: w.color }});
    slide8.addText(w.type, { x: x, y: 1.4, w: 2.9, h: 0.4, fontSize: 18, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
    slide8.addText("优点：" + w.pros, { x: x + 0.15, y: 2.1, w: 2.6, h: 0.8, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.success });
    slide8.addText("缺点：" + w.cons, { x: x + 0.15, y: 3, w: 2.6, h: 0.8, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.danger });
    slide8.addText("适用：" + w.users, { x: x + 0.15, y: 3.9, w: 2.6, h: 0.8, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary });
  });
  
  slide8.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide8.addText("8", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 交易原理
  const slide9 = pres.addSlide();
  slide9.background = { color: theme.bg };
  slide9.addText("交易原理与Gas费", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  // 交易流程图
  slide9.addShape(pres.shapes.OVAL, { x: 0.5, y: 2, w: 1.5, h: 1.5, fill: { color: theme.accent }});
  slide9.addText("发送方", { x: 0.5, y: 2.55, w: 1.5, h: 0.4, fontSize: 14, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  
  slide9.addText("→", { x: 2.2, y: 2.5, w: 0.6, h: 0.5, fontSize: 24, fontFace: "Arial", color: theme.secondary });
  
  slide9.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 3, y: 1.8, w: 3, h: 1.9, fill: { color: theme.light }, rectRadius: 0.1 });
  slide9.addText("交易广播到网络", { x: 3.2, y: 2, w: 2.6, h: 0.4, fontSize: 14, fontFace: "Microsoft YaHei", color: theme.primary, bold: true, align: "center" });
  slide9.addText("矿工打包交易\n确认上链", { x: 3.2, y: 2.5, w: 2.6, h: 0.8, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary, align: "center" });
  
  slide9.addText("→", { x: 6.2, y: 2.5, w: 0.6, h: 0.5, fontSize: 24, fontFace: "Arial", color: theme.secondary });
  
  slide9.addShape(pres.shapes.OVAL, { x: 7, y: 2, w: 1.5, h: 1.5, fill: { color: theme.success }});
  slide9.addText("接收方", { x: 7, y: 2.55, w: 1.5, h: 0.4, fontSize: 14, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  
  // Gas费说明
  slide9.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4, w: 9, h: 1.2, fill: { color: "FFFFFF" }, line: { color: theme.accent, width: 2 }, rectRadius: 0.1 });
  slide9.addText("Gas费（矿工费）", { x: 0.8, y: 4.2, w: 8.4, h: 0.35, fontSize: 16, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  slide9.addText("• 每笔交易需支付Gas费给矿工\n• Gas费越高，交易确认速度越快\n• 侦查提示：Gas费支付地址可能暴露身份", { x: 0.8, y: 4.6, w: 8.4, h: 0.6, fontSize: 12, fontFace: "Microsoft YaHei", color: theme.secondary });
  
  slide9.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide9.addText("9", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 本课小结
  const slide10 = pres.addSlide();
  slide10.background = { color: theme.bg };
  slide10.addText("本课小结", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  
  const summary = [
    "区块链是分布式账本，具有去中心化、不可篡改、透明可追溯的特点",
    "主流虚拟币：BTC（价值存储）、ETH（智能合约）、USDT（稳定币）、XMR（匿名币）",
    "钱包地址由公私钥生成，地址可公开但无法反推私钥",
    "交易需支付Gas费，Gas费支付地址是重要的侦查线索"
  ];
  summary.forEach((s, i) => {
    slide10.addShape(pres.shapes.OVAL, { x: 0.7, y: 1.4 + i * 0.95, w: 0.35, h: 0.35, fill: { color: theme.accent }});
    slide10.addText((i + 1).toString(), { x: 0.7, y: 1.4 + i * 0.95, w: 0.35, h: 0.35, fontSize: 14, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
    slide10.addText(s, { x: 1.3, y: 1.35 + i * 0.95, w: 8, h: 0.7, fontSize: 15, fontFace: "Microsoft YaHei", color: theme.primary });
  });
  
  slide10.addShape(pres.shapes.OVAL, { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fill: { color: theme.accent }});
  slide10.addText("10", { x: 9.3, y: 5.1, w: 0.4, h: 0.4, fontSize: 12, fontFace: "Arial", color: "FFFFFF", bold: true, align: "center", valign: "middle" });
  
  // 结束页
  const slide11 = pres.addSlide();
  slide11.background = { color: theme.primary };
  slide11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  slide11.addText("感谢聆听", { x: 0.5, y: 2.2, w: 9, h: 0.8, fontSize: 48, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  slide11.addText("下节课预告：虚拟币洗钱侦查技术", { x: 0.5, y: 3.2, w: 9, h: 0.5, fontSize: 18, fontFace: "Microsoft YaHei", color: theme.accent, align: "center" });
  slide11.addText("刑侦总队六支队", { x: 0.5, y: 4.5, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  pres.writeFile({ fileName: "C:\\Users\\10127\\WorkBuddy\\Claw\\课程资料\\电信诈骗虚拟币洗钱侦察\\PPT课件\\第2课时-区块链技术基础与虚拟币原理.pptx" });
  console.log("第2课时PPT已生成！");
}

createLesson2();
