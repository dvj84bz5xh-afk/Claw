// slides/compile.js
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

// Vibrant Orange Mint theme (Palette #17)
const theme = {
  primary: "2ec4b6",     // teal for titles (primary)
  secondary: "ff9f1c",   // orange for key content
  accent: "ffbf69",      // light orange for emphasis
  light: "cbf3f0",       // mint green for light background
  bg: "ffffff"           // white background
};

// Import and create each slide
try {
  // Slide 1: Cover
  const slide01 = require('./slide-01.js');
  slide01.createSlide(pres, theme);
  
  // Slide 2: TOC
  const slide02 = require('./slide-02.js');
  slide02.createSlide(pres, theme);
  
  // Slide 3: Unit Objectives
  const slide03 = require('./slide-03.js');
  slide03.createSlide(pres, theme);
  
  // Slide 4: Teaching Activity - Scenario Introduction
  const slide04 = require('./slide-04.js');
  slide04.createSlide(pres, theme);
  
  // Slide 5: Teaching Activity - Listening & Reading
  const slide05 = require('./slide-05.js');
  slide05.createSlide(pres, theme);
  
  // Slide 6: Teaching Activity - Language Exploration
  const slide06 = require('./slide-06.js');
  slide06.createSlide(pres, theme);
  
  // Slide 7: Teaching Activity - Transfer & Innovation
  const slide07 = require('./slide-07.js');
  slide07.createSlide(pres, theme);
  
  // Slide 8: Technology Application - Teaching Assistant
  const slide08 = require('./slide-08.js');
  slide08.createSlide(pres, theme);
  
  // Slide 9: Technology Application - Evaluation & Detection
  const slide09 = require('./slide-09.js');
  slide09.createSlide(pres, theme);
  
  // Slide 10: Technology Application - Homework Assistant
  const slide10 = require('./slide-10.js');
  slide10.createSlide(pres, theme);
  
  // Slide 11: Expert Evaluation
  const slide11 = require('./slide-11.js');
  slide11.createSlide(pres, theme);
  
  // Slide 12: Summary
  const slide12 = require('./slide-12.js');
  slide12.createSlide(pres, theme);
  
  console.log('All slides created successfully.');
} catch (error) {
  console.error('Error creating slides:', error);
  process.exit(1);
}

// Write the presentation to file
pres.writeFile({ fileName: './output/小学英语单元整体教学课件.pptx' })
  .then(() => {
    console.log('Presentation saved: ./output/小学英语单元整体教学课件.pptx');
  })
  .catch(err => {
    console.error('Error saving presentation:', err);
  });