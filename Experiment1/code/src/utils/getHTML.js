const https = require('https')

/**
 * 获取爬虫html
 * @param {*} url 爬虫地址
 * @returns {string} html
 */
async function getHTML(url) {
    return new Promise((resolve) => {
        https.get(url, (res) => {
            let html = ''

            res.on('data', (chunk) => {
                html += chunk
            })

            res.on('end', () => {
                resolve(html)
            })
        })
    })
}


module.exports = getHTML