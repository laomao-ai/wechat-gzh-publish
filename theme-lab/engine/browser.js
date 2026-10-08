// 统一找浏览器：优先 CHROME 环境变量，其次本机常见 Chrome 路径，都没有就用 Playwright 自带 Chromium。
const fs = require('fs');
const { chromium } = require('playwright');
const CANDIDATES = [
  process.env.CHROME,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
];
module.exports.launch = () => {
  const exe = CANDIDATES.find(p => p && fs.existsSync(p));
  return chromium.launch(exe ? { executablePath: exe } : {});
};
