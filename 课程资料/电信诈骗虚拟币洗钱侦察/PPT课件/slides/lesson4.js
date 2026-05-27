const pptxgen = require("pptxgenjs");
const theme = { primary: "1a365d", secondary: "2c5282", accent: "3182ce", light: "bee3f8", bg: "f7fafc", danger: "c53030", success: "276749", warning: "c05621" };

function createLesson4() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  pres.author = '刑侦总队六支队';
  
  // 封面
  const s1 = pres.addSlide();
  s1.background = { color: theme.primary };
  s1.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  s1.addText("案件侦查实务", { x: 0.5, y: 1.8, w: 9, h: 0.8, fontSize: 44, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  s1.addText("与综合应用", { x: 0.5, y: 2.6, w: 9, h: 0.8, fontSize: 44, fontFace: "Microsoft YaHei", color: theme.accent, bold: true, align: "center" });
  s1.addText("第4课时", { x: 0.5, y: 3.6, w: 9, h: 0.5, fontSize: 20, fontFace: "Microsoft YaHei", color: "E2E8F0", align: "center" });
  s1.addText("刑侦总队六支队", { x: 0.5, y: 4.8, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  // 目录
  const s2 = pres.addSlide();
  s2.background = { color: theme.bg };
  s2.addText("本课时内容", { x: 0.5, y: 0.5, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const toc = [{n:"01",t:"案件线索发现",d:"从接报案到初查"},{n:"02",t:"证据固定规范",d:"电子证据收集与保全"},{n:"03",t:"跨境协作机制",d:"国际司法与交易所协作"},{n:"04",t:"综合演练",d:"模拟案例分析"}];
  toc.forEach((item,i)=>{const y=1.4+i; s2.addShape(pres.shapes.OVAL,{x:0.8,y,w:0.6,h:0.6,fill:{color:theme.accent}}); s2.addText(item.n,{x:0.8,y,w:0.6,h:0.6,fontSize:18,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s2.addText(item.t,{x:1.7,y:y+0.05,w:7,h:0.35,fontSize:22,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s2.addText(item.d,{x:1.7,y:y+0.4,w:7,h:0.3,fontSize:14,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s2.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s2.addText("2",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 线索发现流程
  const s3 = pres.addSlide();
  s3.background = { color: theme.bg };
  s3.addText("案件线索发现流程", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const flow = ["受害人报案","获取转账记录","提取涉案地址","链上初查","紧急止付","立案侦查"];
  flow.forEach((f,i)=>{const x=0.3+i*1.55; s3.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:2.2,w:1.4,h:1.2,fill:{color:i%2==0?theme.accent:theme.secondary},rectRadius:0.1}); s3.addText(f,{x,y:2.65,w:1.4,h:0.5,fontSize:11,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true,align:"center"}); if(i<5)s3.addText("→",{x:x+1.4,y:2.7,w:0.15,h:0.4,fontSize:16,fontFace:"Arial",color:theme.secondary});});
  s3.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4,w:9,h:1.2,fill:{color:theme.light}});
  s3.addText("紧急处置要点：",{x:0.7,y:4.1,w:2,h:0.3,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary,bold:true});
  s3.addText("1.立即查询受害人转账记录 2.快速获取涉案地址 3.监控地址动态 4.联系交易所冻结 5.及时固定电子证据",{x:0.7,y:4.45,w:8.6,h:0.6,fontSize:12,fontFace:"Microsoft YaHei",color:theme.secondary});
  s3.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s3.addText("3",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 证据固定
  const s4 = pres.addSlide();
  s4.background = { color: theme.bg };
  s4.addText("电子证据固定规范", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const evidences = [
    {t:"区块链存证",d:"使用保全网、蚂蚁区块链等存证平台"},
    {t:"截图取证",d:"完整截图包含URL、时间、内容"},
    {t:"录屏取证",d:"动态操作过程全程录屏"},
    {t:"司法保全",d:"申请法院证据保全令"},
    {t:"鉴定意见",d:"委托专业机构出具鉴定报告"}
  ];
  evidences.forEach((e,i)=>{const y=1.2+i*0.78; s4.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.7,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s4.addText(e.t,{x:0.8,y:y+0.15,w:2,h:0.4,fontSize:15,fontFace:"Microsoft YaHei",color:theme.accent,bold:true}); s4.addText(e.d,{x:3,y:y+0.18,w:6.3,h:0.4,fontSize:13,fontFace:"Microsoft YaHei",color:theme.primary});});
  s4.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s4.addText("4",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 法律文书
  const s5 = pres.addSlide();
  s5.background = { color: theme.bg };
  s5.addText("常用法律文书", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const docs = [{n:"调取证据通知书",t:"向交易所调取注册信息、交易记录、KYC资料",to:"虚拟币交易所"},{n:"冻结通知书",t:"要求交易所冻结涉案账户及资产",to:"虚拟币交易所"},{n:"协助查询函",t:"请求链上数据分析平台提供技术支持",to:"知帆科技/中科链安"},{n:"司法鉴定委托书",t:"委托鉴定机构出具区块链证据鉴定意见",to:"司法鉴定中心"}];
  docs.forEach((d,i)=>{const y=1.15+i*1; s5.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.95,fill:{color:"FFFFFF"},line:{color:theme.accent,width:1},rectRadius:0.1}); s5.addText(d.n,{x:0.8,y:y+0.1,w:2.5,h:0.35,fontSize:15,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s5.addText(d.to,{x:0.8,y:y+0.5,w:2.5,h:0.3,fontSize:11,fontFace:"Microsoft YaHei",color:theme.accent}); s5.addText(d.t,{x:3.5,y:y+0.2,w:5.8,h:0.6,fontSize:12,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s5.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s5.addText("5",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 证据链
  const s6 = pres.addSlide();
  s6.background = { color: theme.bg };
  s6.addText("证据链构建", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const chain = ["受害人陈述与报案材料","银行转账流水记录","虚拟币交易记录（链上数据）","涉案地址分析报告","资金流向图","嫌疑人身份信息","聊天记录/通话记录","嫌疑人供述与辩解"];
  chain.forEach((c,i)=>{const x=0.5+(i%2)*4.8; const y=1.2+Math.floor(i/2)*0.95; s6.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.5,h:0.8,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s6.addShape(pres.shapes.OVAL,{x:x+0.1,y:y+0.25,w:0.3,h:0.3,fill:{color:theme.accent}}); s6.addText((i+1).toString(),{x:x+0.1,y:y+0.25,w:0.3,h:0.3,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s6.addText(c,{x:x+0.5,y:y+0.25,w:3.8,h:0.4,fontSize:13,fontFace:"Microsoft YaHei",color:theme.primary});});
  s6.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.8,w:9,h:0.5,fill:{color:theme.light}}); s6.addText("完整的证据链是定罪量刑的基础，必须形成相互印证的证据体系",{x:0.7,y:4.9,w:8.6,h:0.3,fontSize:13,fontFace:"Microsoft YaHei",color:theme.primary});
  s6.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s6.addText("6",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 跨境协作
  const s7 = pres.addSlide();
  s7.background = { color: theme.bg };
  s7.addText("跨境协作机制", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const cross = [{t:"国际刑警组织",d:"通过INTERPOL发布红色通缉令，协调多国警方合作"},{t:"双边司法协助",d:"依据双边条约开展证据交换、嫌疑人引渡"},{t:"交易所合规",d:"大型交易所设有合规部门，可配合司法调查"},{t:"金融情报交换",d:"通过FIU渠道交换涉虚拟货币犯罪情报"}];
  cross.forEach((c,i)=>{const y=1.2+i*0.98; s7.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.9,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s7.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:0.15,h:0.9,fill:{color:theme.accent}}); s7.addText(c.t,{x:0.8,y:y+0.15,w:3,h:0.4,fontSize:16,fontFace:"Microsoft YaHei",color:theme.primary,bold:true}); s7.addText(c.d,{x:4,y:y+0.2,w:5.3,h:0.5,fontSize:13,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s7.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s7.addText("7",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 实战案例
  const s8 = pres.addSlide();
  s8.background = { color: theme.bg };
  s8.addText("典型案例：某电诈集团虚拟币洗钱案", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 28, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  s8.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y:1.2,w:4.4,h:3.8,fill:{color:theme.primary},rectRadius:0.15});
  s8.addText("案情简介",{x:0.7,y:1.4,w:4,h:0.4,fontSize:16,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true});
  const info = ["类型：虚假投资理财","金额：8.2亿元","受害人：3200余人","洗钱：USDT+混币器+OTC"];
  info.forEach((t,i)=>{s8.addText("• "+t,{x:0.9,y:1.95+i*0.5,w:4,h:0.4,fontSize:12,fontFace:"Microsoft YaHei",color:"E2E8F0"});});
  s8.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.1,y:1.2,w:4.4,h:3.8,fill:{color:"FFFFFF"},line:{color:theme.accent,width:2},rectRadius:0.15});
  s8.addText("侦查过程",{x:5.3,y:1.4,w:4,h:0.4,fontSize:16,fontFace:"Microsoft YaHei",color:theme.primary,bold:true});
  const proc = ["① 受害人报案，获取转账记录","② 提取12个涉案USDT地址","③ 链上追踪，绘制资金流向","④ 识别混币器和OTC交易所","⑤ 调取交易所KYC信息","⑥ 锁定嫌疑人身份，实施抓捕"];
  proc.forEach((p,i)=>{s8.addText(p,{x:5.4,y:1.95+i*0.55,w:4,h:0.5,fontSize:11,fontFace:"Microsoft YaHei",color:theme.secondary});});
  s8.addShape(pres.shapes.RECTANGLE,{x:0.5,y:4.8,w:9,h:0.5,fill:{color:theme.light}}); s8.addText("战果：抓获犯罪嫌疑人47名，追回赃款1.2亿元",{x:0.7,y:4.9,w:8.6,h:0.3,fontSize:13,fontFace:"Microsoft YaHei",color:theme.success});
  s8.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s8.addText("8",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 综合演练
  const s9 = pres.addSlide();
  s9.background = { color: theme.bg };
  s9.addText("综合演练：模拟案件分析", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  s9.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y:1.2,w:9,h:3.8,fill:{color:"FFFFFF"},line:{color:theme.accent,width:2},rectRadius:0.15});
  s9.addText("演练任务",{x:0.7,y:1.4,w:8.6,h:0.4,fontSize:18,fontFace:"Microsoft YaHei",color:theme.accent,bold:true});
  const tasks = ["根据提供的受害人报案材料和转账记录，提取涉案虚拟币地址","使用区块链浏览器查询地址交易记录，绘制资金流向图","分析资金去向，识别混币器和交易所","提出侦查方案，包括线索发现和证据固定措施"];
  tasks.forEach((t,i)=>{s9.addShape(pres.shapes.OVAL,{x:0.9,y:1.95+i*0.7,w:0.3,h:0.3,fill:{color:theme.accent}}); s9.addText((i+1).toString(),{x:0.9,y:1.95+i*0.7,w:0.3,h:0.3,fontSize:11,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"}); s9.addText(t,{x:1.4,y:1.9+i*0.7,w:7.9,h:0.6,fontSize:13,fontFace:"Microsoft YaHei",color:theme.primary});});
  s9.addShape(pres.shapes.RECTANGLE,{x:0.7,y:4.7,w:8.6,h:0.7,fill:{color:theme.light}}); s9.addText("分组进行，每组提交分析报告，教官点评",{x:0.9,y:4.85,w:8.2,h:0.4,fontSize:14,fontFace:"Microsoft YaHei",color:theme.secondary});
  s9.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s9.addText("9",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 课程总回顾
  const s10 = pres.addSlide();
  s10.background = { color: theme.bg };
  s10.addText("课程总回顾", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  const review = [{t:"第1课时",d:"电信诈骗概述与虚拟币洗钱趋势"},{t:"第2课时",d:"区块链技术基础与虚拟币原理"},{t:"第3课时",d:"虚拟币洗钱侦查技术"},{t:"第4课时",d:"案件侦查实务与综合应用"}];
  review.forEach((r,i)=>{const y=1.2+i*0.95; s10.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y,w:9,h:0.85,fill:{color:"FFFFFF"},line:{color:theme.light,width:1},rectRadius:0.1}); s10.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:2,h:0.85,fill:{color:theme.accent}}); s10.addText(r.t,{x:0.5,y:y+0.25,w:2,h:0.4,fontSize:14,fontFace:"Microsoft YaHei",color:"FFFFFF",bold:true,align:"center"}); s10.addText(r.d,{x:2.7,y:y+0.25,w:6.6,h:0.4,fontSize:15,fontFace:"Microsoft YaHei",color:theme.primary});});
  s10.addShape(pres.shapes.RECTANGLE,{x:0.5,y:5,w:9,h:0.5,fill:{color:theme.primary}}); s10.addText("核心能力：掌握链上追踪技术，规范固定电子证据，依法打击虚拟币洗钱犯罪",{x:0.7,y:5.1,w:8.6,h:0.3,fontSize:13,fontFace:"Microsoft YaHei",color:"FFFFFF"});
  s10.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s10.addText("10",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 课后作业
  const s11 = pres.addSlide();
  s11.background = { color: theme.bg };
  s11.addText("课后作业", { x: 0.5, y: 0.4, w: 9, h: 0.6, fontSize: 32, fontFace: "Microsoft YaHei", color: theme.primary, bold: true });
  s11.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.5,y:1.2,w:9,h:3.8,fill:{color:"FFFFFF"},line:{color:theme.accent,width:2},rectRadius:0.15});
  s11.addText("作业要求",{x:0.7,y:1.4,w:8.6,h:0.4,fontSize:18,fontFace:"Microsoft YaHei",color:theme.accent,bold:true});
  const hw = ["选择一起虚拟币洗钱典型案例（可使用本课程案例）","撰写完整的侦查分析报告，包括：","  - 案件基本情况梳理","  - 资金流向详细分析","  - 侦查过程与措施","  - 证据固定要点","  - 经验总结与启示"];
  hw.forEach((h,i)=>{s11.addText(h,{x:0.9,y:1.9+i*0.55,w:8.4,h:0.5,fontSize:14,fontFace:"Microsoft YaHei",color:theme.primary});});
  s11.addShape(pres.shapes.RECTANGLE,{x:0.7,y:4.7,w:8.6,h:0.7,fill:{color:theme.light}}); s11.addText("提交要求：Word文档，字数不少于3000字，一周内提交",{x:0.9,y:4.85,w:8.2,h:0.4,fontSize:13,fontFace:"Microsoft YaHei",color:theme.secondary});
  s11.addShape(pres.shapes.OVAL,{x:9.3,y:5.1,w:0.4,h:0.4,fill:{color:theme.accent}}); s11.addText("11",{x:9.3,y:5.1,w:0.4,h:0.4,fontSize:12,fontFace:"Arial",color:"FFFFFF",bold:true,align:"center",valign:"middle"});
  
  // 结束
  const s12 = pres.addSlide();
  s12.background = { color: theme.primary };
  s12.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.1, fill: { color: theme.accent }});
  s12.addText("课程结束", { x: 0.5, y: 2, w: 9, h: 0.8, fontSize: 48, fontFace: "Microsoft YaHei", color: "FFFFFF", bold: true, align: "center" });
  s12.addText("感谢聆听，祝工作顺利", { x: 0.5, y: 3, w: 9, h: 0.5, fontSize: 20, fontFace: "Microsoft YaHei", color: theme.accent, align: "center" });
  s12.addText("打击犯罪，保护人民", { x: 0.5, y: 3.8, w: 9, h: 0.5, fontSize: 18, fontFace: "Microsoft YaHei", color: "E2E8F0", align: "center" });
  s12.addText("刑侦总队六支队", { x: 0.5, y: 4.5, w: 9, h: 0.4, fontSize: 16, fontFace: "Microsoft YaHei", color: "A0AEC0", align: "center" });
  
  pres.writeFile({ fileName: "C:\\Users\\10127\\WorkBuddy\\Claw\\课程资料\\电信诈骗虚拟币洗钱侦察\\PPT课件\\第4课时-案件侦查实务与综合应用.pptx" });
  console.log("第4课时PPT已生成！");
}

createLesson4();
