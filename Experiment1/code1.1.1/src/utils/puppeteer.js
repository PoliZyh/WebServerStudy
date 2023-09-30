const puppeteer = require('puppeteer');
const browserPool = require('./browser-pool');


/**
 * 滚动到底部
 * @param {} page 
 */
async function autoScroll(page) {
    console.log('正在滚动页面,时间较长请稍等...')
    await page.evaluate(async () => {
        await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 100;
            const scrollInterval = setInterval(() => {
                const scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;
                if (totalHeight >= scrollHeight) {
                    clearInterval(scrollInterval);
                    console.log('滚动页面结束...')
                    resolve();
                }
            }, 100);
        });
    });
}


/**
 * 优化
 * 使用链接池
 */
async function runPuppeteerScriptForTexts(urls, classTag) {
    // console.log(`开始爬取${url}的Text`)
    return new Promise(async (resolve) => {
        const browser = await browserPool.acquire(); // 从连接池获取浏览器实例

        const page = await browser.newPage();
        await page.setDefaultNavigationTimeout(60000);

        const dynamicContents = []

        for (const urlItem in urls) {
            console.log(`开始爬取${urls[urlItem]}的Text`)
            await page.goto(urls[urlItem]);
            await page.waitForSelector(classTag);
            const dynamicContent = await page.evaluate((classTag) => {
                const element = document.querySelector(classTag);
                return element ? element.textContent : null;
            }, classTag);
            dynamicContents.push(dynamicContent)
            console.log(`结束爬取${urls[urlItem]}的Text`)
        }

        // 关闭页面
        await page.close();
    
        // 将浏览器实例返回连接池
        browserPool.release(browser);

        resolve(
            dynamicContents
        )
    })
}


async function runPuppeteerScript(url, classTag, classTagText, classTagDate, classTagName) {
    console.log(`开始爬取${url}的Text和href`)
    return new Promise(async (resolve) => {
        const browser = await browserPool.acquire(); // 从连接池获取浏览器实例

        const page = await browser.newPage();
        await page.goto(url);
        await page.click('.btn-load.m-c-bg-color-white.m-c-color-gray.btn-middle');
        // 模拟滚动到底部
        await autoScroll(page);
        await page.waitForSelector(classTag);

        // 执行其他 Puppeteer 操作...
        const dynamicHrefs = await page.evaluate((classTag) => {
            const elements = document.querySelectorAll(classTag);
            const data = []
            elements.forEach(element => {
                data.push(element.getAttribute('href'))
            })
            return data
        }, classTag);

        const dynamicContents = await page.evaluate((classTagText) => {
            const elements = document.querySelectorAll(classTagText);
            const data = []
            elements.forEach(element => {
                data.push(element.textContent)
            })
            return data
        }, classTagText)

        const dynamicDates = await page.evaluate((classTagDate) => {
            const elements = document.querySelectorAll(classTagDate);
            console.log(elements)
            const data = []
            elements.forEach(element => {
                data.push(element.textContent)
            })
            return data
        }, classTagDate)

        const dynamicNames = await page.evaluate((classTagName) => {
            const elements = document.querySelectorAll(classTagName);
            console.log(elements)
            const data = []
            elements.forEach(element => {
                data.push(element.textContent)
            })
            return data
        }, classTagName)

        // 关闭页面
        await page.close();
        console.log(`结束爬取${url}的Text和Href`)

        // 将浏览器实例返回连接池
        browserPool.release(browser);

        resolve({
            dynamicHrefs,
            dynamicContents,
            dynamicDates,
            dynamicNames
        })
    })
}


module.exports = {
    runPuppeteerScript,
    runPuppeteerScriptForTexts
}