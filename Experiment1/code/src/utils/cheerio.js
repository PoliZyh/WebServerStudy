const cheerio = require('cheerio')

/**
 * 爬取href属性
 * @param {*} html html字符串
 * @param {*} classTag 类名
 * @returns hrefs
 */
function getHrefsByTagClass(html, classTag) {
    console.log(`开始爬取${classTag}中...`)
    const $ = cheerio.load(html)
    const resHrefs = []
    $(classTag).each(function() {
        const href = $(this).attr('href')
        if (href) {
            resHrefs.push(href)
        }
    })
    console.log(`结束爬取${classTag}...`)
    return resHrefs
}

/**
 * 爬取文本内容
 * @param {*} html html字符串
 * @param {*} classTag 类名
 * @returns 
 */
function getContentByTagClass(html, classTag) {
    console.log(`开始爬取${classTag}中...`)
    const $ = cheerio.load(html)
    const resContent = []
    $(classTag).each(function() {
        const text = $(this).text()
        if (text) {
            resContent.push(text)
        }
    })
    console.log(`结束爬取${classTag}...`)
    return resContent
}


module.exports = {
    getHrefsByTagClass,
    getContentByTagClass
}