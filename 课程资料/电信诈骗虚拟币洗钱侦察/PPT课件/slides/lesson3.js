const pptxgen = require("pptxgenjs");
const theme = { primary: "1a365d", secondary: "2c5282", accent: "3182ce", light: "bee3f8", bg: "f7fafc", danger: "c53030", success: "276749", warning: "c05621" };

function createLesson3() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = '刑侦总队六支队';
  
  // 封面
  const s1 = pres.addSlide();
  s1.background = { color: theme.primary };
  s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  s1.addText("虚拟币洗钱侦查技术", { x: 0.5, y: 2.2, w: 9, h: 0.8, fontSize: 44, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  s1.addText("第3课时", { x: 0.5, y: 3.3, w: 9, h: 0.5, fontSize: 20, fontFace: "Microsoft YaHei", color: "E2E8F0", align: "center" });
  s1.addText("刑侦总队六支队", { x: 0.5, y: 4.8, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  // 目录
  const s2 = pres.addSlide();
  s2.background = { color: theme.bg };
  s2.addText("本课时内容", { x: 0.5, y: 0.5, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const toc = [{n:"01",t:"虚拟币洗钱模式",d:"常见洗钱手法解析"},{n:"02",t:"链上资金追踪",d:"交易哈希与地址分析"},{n:"03",t:"区块链分析工具",d:"浏览器与专业平台"},{n:"04",t:"混币器破解",d:"Tornado Cash识别方法"}];
  toc.forEach((item,i)=>{const y=1.4+i; s2.addShape(pres.shapes.OVAL,{x:0.8,y,w:0.6,h:0.6,fill:{color:theme.accent}}); s2.addText(item.n,{x:0.8,y,w:0.6,h:0.6,fontSize:18,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s2.addText(item.t,{x:1.7,y:y+0.05,w:7,h:0.35,fontSize:22,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s2.addText(item.d,{x:1.7,y:y+0.4,w:7,h:0.3,fontSize:14,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s2.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s2.addText("2",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 洗钱模式
  const s3 = pres.addSlide();
  s3.background = { color: theme.bg };
  s3.addText("虚拟币洗钱常见模式", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const modes = [{t:"直接转移",d:"受害人直接转账到犯罪地址",c:theme.danger},{t:"分层清洗",d:"多层转账切断资金链条",c:theme.warning},{t:"混币器",d:"Tornado Cash等切断追踪",c:theme.danger},{t:"OTC交易",d:"场外交易兑换法币",c:theme.secondary}];
  modes.forEach((m,i)=>{const y=1.3+i*0.95; s3.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.85,fill:{color:"FFFFFF"},line:{color:m.c,width:2},rectRadius:0.1}); s3.addText(m.t,{x:0.8,y:y+0.15,w:2.5,h:0.5,fontSize:18,fontFace:"Microsoft YaHei",color:m.c,bold:true}); s3.addText(m.d,{x:3.5,y:y+0.25,w:5.8,h:0.4,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary});});
  s3.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s3.addText("3",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 资金流向图
  const s4 = pres.addSlide();
  s4.background = { color: theme.bg };
  s4.addText("典型洗钱资金流向", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const flow = ["受害人","犯罪地址","中转地址","混币器","OTC交易所","法币提现"];
  flow.forEach((f,i)=>{const x=0.3+i*1.55; s4.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:2.5,w:1.4,h:1,fill:{color:i%2==0?theme.accent:theme.secondary},rectRadius:0.1}); s4.addText(f,{x,y:2.85,w:1.4,h:0.4,fontSize:11,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true,align:"center"}); if(i<5)s4.addText("→",{x:x+1.4,y:2.85,w:0.15,h:0.4,fontSize:16,fontFace:"Arial",color:theme.secondary});});
  s4.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4,w:9,h:1.2,fill:{color:theme.light}});
  s4.addText("侦查要点：在混币前截断、关注OTC交易所KYC、追踪法币出金渠道",{x:0.7,y:4.3,w:8.6,h:0.6,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary});
  s4.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s4.addText("4",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 链上追踪方法
  const s5 = pres.addSlide();
  s5.background = { color: theme.bg };
  s5.addText("链上资金追踪方法", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const methods = [{t:"交易哈希追踪",d:"通过TxHash查询交易详情、金额、时间、收发地址"},{t:"地址聚类分析",d:"识别同一主体的多个地址，绘制地址关系图"},{t:"资金流向图",d:"可视化展示资金流动路径，识别关键节点"},{t:"时间戳分析",d:"分析交易时间规律，寻找关联证据"}];
  methods.forEach((m,i)=>{const y=1.3+i*0.95; s5.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.85,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s5.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:0.15,h:0.85,fill:{color:theme.accent}}); s5.addText(m.t,{x:0.8,y:y+0.15,w:3,h:0.4,fontSize:16,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s5.addText(m.d,{x:4,y:y+0.2,w:5.3,h:0.5,fontSize:13,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s5.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s5.addText("5",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 追踪步骤
  const s6 = pres.addSlide();
  s6.background = { color: theme.bg };
  s6.addText("链上追踪六步法", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const steps = ["获取涉案交易哈希(TxHash)","在区块链浏览器查询交易详情","分析输入输出地址关系","标记地址标签（交易所、混币器等）","绘制完整资金流向图","追溯资金来源和去向"];
  steps.forEach((s,i)=>{const y=1.2+i*0.7; s6.addShape(pres.shapes.OVAL,{x:0.8,y:y,w:0.5,h:0.5,fill:{color:theme.accent}}); s6.addText((i+1).toString(),{x:0.8,y:y,w:0.5,h:0.5,fontSize:16,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s6.addText(s,{x:1.5,y:y+0.05,w:8,h:0.45,fontSize:16,fontFace:"Microsoft YaHei",color:theme.primary});});
  s6.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s6.addText("6",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 区块链浏览器
  const s7 = pres.addSlide();
  s7.background = { color: theme.bg };
  s7.addText("区块链浏览器使用", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const browsers = [{n:"Etherscan",d:"以太坊官方浏览器，支持ERC20代币追踪",u:"etherscan.io"},{n:"BSCScan",d:"币安智能链浏览器，BSC生态专用",u:"bscscan.com"},{n:"OKLink",d:"欧科云链，支持多链查询",u:"oklink.com"},{n:"Blockchain.com",d:"比特币浏览器，BTC专用",u:"blockchain.com"}];
  browsers.forEach((b,i)=>{const y=1.2+i*1; s7.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.9,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s7.addText(b.n,{x:0.8,y:y+0.15,w:2.5,h:0.4,fontSize:18,fontFace:"Microsoft YaHei",color:theme.accent,bold:true}); s7.addText(b.d,{x:3.5,y:y+0.15,w:4,h:0.4,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary}); s7.addText(b.u,{x:8,y:y+0.2,w:1.4,h:0.35,fontSize:11,fontFace:"Courier New",color:theme.secondary});});
  s7.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s7.addText("7",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 专业工具
  const s8 = pres.addSlide();
  s8.background = { color: theme.bg };
  s8.addText("专业区块链分析平台", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const tools = [{n:"知帆科技",d:"CHAINDIGG，国内领先的区块链大数据分析平台",f:"地址标签库、资金流向图、智能分析"},{n:"中科链安",d:"专注于链上安全与虚拟币犯罪治理",f:"风险地址识别、交易监控、案件协查"},{n:"欧科云链",d:"OKLink Onchain，多链数据分析",f:"链上监控、大额预警、地址画像"},{n:"Chainalysis",d:"国际知名区块链分析公司",f:"Reactor资金追踪、KYT风险识别"}];
  tools.forEach((t,i)=>{const y=1.1+i*0.98; s8.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.9,fill:{color:"FFFFFF"},line:{color:theme.accent,width:1},rectRadius:0.1}); s8.addText(t.n,{x:0.8,y:y+0.1,w:2,h:0.35,fontSize:16,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s8.addText(t.d,{x:0.8,y:y+0.48,w:8.4,h:0.25,fontSize:12,fontFace:"Microsoft YaHei",color:theme.secondary}); s8.addShape(pres.shapes.RECTANGLE,{x:3,y:y+0.1,w:6,h:0.3,fill:{color:theme.light}}); s8.addText(t.f,{x:3.1,y:y+0.13,w:5.8,h:0.25,fontSize:11,fontFace:"Microsoft YaHei",color:theme.primary});});
  s8.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s8.addText("8",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 混币器
  const s9 = pres.addSlide();
  s9.background = { color: theme.bg };
  s9.addText("混币器原理与识别", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  s9.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y:1.3,w:9,h:3.8,fill:{color:"FFFFFF"},line:{color:theme.danger,width:2},rectRadius:0.15});
  s9.addText("Tornado Cash",{x:0.7,y:1.5,w:8.6,h:0.4,fontSize:20,fontFace:"Microsoft YaHei",color:theme.danger,bold:true});
  s9.addText("原理：使用零知识证明技术，将多笔资金混合存入资金池，再提取时无法追溯资金来源",{x:0.9,y:2,w:8.2,h:0.6,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary});
  const tc = ["多用户将资金存入智能合约","合约生成存款凭证（Note）","用户凭凭证提取资金","提取地址与存入地址无关联"];
  tc.forEach((t,i)=>{s9.addShape(pres.shapes.OVAL,{x:1,y:2.8+i*0.5,w:0.3,h:0.3,fill:{color:theme.danger}}); s9.addText(t,{x:1.5,y:2.75+i*0.5,w:7.5,h:0.35,fontSize:13,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s9.addShape(pres.shapes.RECTANGLE,{x:0.7,y:4.7,w:8.6,h:0.4,fill:{color:theme.light}}); s9.addText("破解思路：存取款时间分析、金额匹配、IP地址追踪、交易所提币KYC",{x:0.9,y:4.75,w:8.2,h:0.3,fontSize:12,fontFace:"Microsoft YaHei",color:theme.primary});
  s9.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s9.addText("9",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 小结
  const s10 = pres.addSlide();
  s10.background = { color: theme.bg };
  s10.addText("本课小结", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const sum = ["虚拟币洗钱模式：直接转移、分层清洗、混币器、OTC交易","链上追踪六步法：从交易哈希到资金流向图","区块链浏览器：Etherscan、BSCScan、OKLink等","专业工具：知帆科技、中科链安等平台","混币器破解：时间分析、金额匹配、KYC追踪"];
  sum.forEach((s,i)=>{s10.addShape(pres.shapes.OVAL,{x:0.7,y:1.3+i*0.75,w:0.35,h:0.35,fill:{color:theme.accent}}); s10.addText((i+1).toString(),{x:0.7,y:1.3+i*0.75,w:0.35,h:0.35,fontSize:14,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s10.addText(s,{x:1.3,y:1.25+i*0.75,w:8,h:0.6,fontSize:15,fontFace:"Microsoft YaHei",color:theme.primary});});
  s10.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s10.addText("10",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 结束
  const s11 = pres.addSlide();
  s11.background = { color: theme.primary };
  s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  s11.addText("感谢聆听", { x: 0.5, y: 2.2, w: 9, h: 0.8, fontSize: 48, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  s11.addText("下节课预告：案件侦查实务与综合应用", { x: 0.5, y: 3.2, w: 9, h: 0.5, fontSize: 18, fontFace: "Microsoft YaHei", color: theme.accent, align: "center" });
  s11.addText("刑侦总队六支队", { x: 0.5, y: 4.5, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  pres.writeFile({ fileName: "C:\\Users\\10127\\WorkBuddy\\Claw\\课程资料\\电信诈骗虚拟币洗钱侦察\\PPT课件\\第3课时-虚拟币洗钱侦查技术.pptx" });
  console.log("第3课时PPT已生成！");
}

createLesson3();
