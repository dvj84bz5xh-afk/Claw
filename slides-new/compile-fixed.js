const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

// 教育主题配色方案 - 温暖活泼适合小学
const theme = {
  primary: "2ec4b6",    // teal - 主标题色
  secondary: "ff9f1c",  // orange - 强调色
  accent: "e71d36",     // red - 重要内容色
  light: "ffbf69",      // light orange - 辅助色
  bg: "f2f2f2"          // light gray - 背景色
};

// 加载所有幻灯片模块
for (let i = 1; i <= 12; i++) {
  const num = String(i).padStart(2, '0');
  try {
    const slideModule = require(`./slide-${num}.js`);
    slideModule.createSlide(pres, theme);
    console.log(`✓ Slide ${num} loaded successfully`);
  } catch (err) {
    console.error(`✗ Error loading slide-${num}.js:`, err.message);
  }
}

console.log('Generating PowerPoint presentation...');

// 生成PPT文件
pres.writeFile({ fileName: './output/上海小学英语单元整体教学课件.pptx' })
  .then(fileName => {
    console.log('\n🎉 PPT生成成功!');
    console.log(`📁 文件位置: ${fileName}`);
    console.log(`📊 幻灯片数量: ${pres.slides.length}`);
  })
  .catch(err => {
    console.error('\n❌ PPT生成失败:');
    console.error(err);
    process.exit(1);
  });