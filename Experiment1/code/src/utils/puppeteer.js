const puppeteer = require('puppeteer');

/**
 * 通过爬虫获取tag指定内容
 * @param {*} url 爬虫地址
 * @param {*} classTag tag类名
 * @returns {Promise} 封装的内容
 */
async function getContentByTagClass(url, classTag) {
    console.log(`开始爬取${url}的Text`)
    return new Promise(async (resolve) => {
        const browser = await puppeteer.launch({
            headless: 'true', 
            args: [
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-first-run',
                '--no-sandbox',
                '--no-zygote',
                '--single-process'
            ]
        });
        const page = await browser.newPage();

        await page.goto(url);
        await page.waitForSelector(classTag); // 等待动态元素加载

        const dynamicContent = await page.evaluate((classTag) => {
            const element = document.querySelector(classTag);
            return element ? element.textContent : null;
        }, classTag);

        await browser.close()
        console.log(`结束爬取${classTag}的Text`)

        resolve(
            dynamicContent
        )
    })
}


async function getHrefsByTagClass(url, classTag) {
    console.log(`开始爬取${url}的hrefs`)
    return new Promise(async (resolve) => {
        const browser = await puppeteer.launch({headless: 'new', timeout: 60000});
        const page = await browser.newPage();

        await page.goto(url);
        
        await page.waitForSelector(classTag);

        const hrefAttributeValue = await page.evaluate((classTag) => {
            const hrefValues = [];
            const elements = document.querySelectorAll(classTag)
            elements.forEach((element) => {
                const href = element.getAttribute('href');
                if (href) {
                    hrefValues.push(href);
                }
            });
            return hrefValues // href数组
        }, classTag);

        await browser.close()

        console.log(`结束爬取${classTag}的hrefs`)
        resolve(hrefAttributeValue)
    })
}



module.exports = {
    getContentByTagClass,
    getHrefsByTagClass
}

