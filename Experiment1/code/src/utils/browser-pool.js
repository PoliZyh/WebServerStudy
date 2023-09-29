const puppeteer = require('puppeteer');
const genericPool = require('generic-pool')
// 创建一个浏览器工厂
const browserFactory = {
  create: async () => {
    const browser = await puppeteer.launch();
    return browser;
  },
  destroy: (browser) => {
    browser.close();
  },
};

// 创建浏览器连接池
const browserPool = genericPool.createPool(browserFactory, { min: 1, max: 10 }); // 可根据需求调整最小和最大连接数

module.exports = browserPool;
