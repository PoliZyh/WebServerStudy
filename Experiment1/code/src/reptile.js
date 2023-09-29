
const api = require('./api/setting')
const day = require('./utils/day.js')
const myPuppeteer = require('./utils/puppeteer.js')
const myCheerio = require('./utils/cheerio')
const getHTML = require('./utils/getHTML')
const tagClasses = require('./tagClasses')

/**
 * 获取直播间url地址以及比赛名字
 * @returns 
 */
async function getDatePage() {
    // 用来存储直播间界面的url
    const liveUrl = {}
    const rootApi = api.API_ROOT
    // 通过day得到2023-09-21 - 今日的日期数组
    const dateArr = day.getAllDateArray()

    console.log('开始爬取直播间的url，请等候...')

    for(const dayItem of dateArr) {
        const url = rootApi + dayItem // 拼接url

        const html = await getHTML(url)
        const hrefs = myCheerio.getHrefsByTagClass(html, tagClasses.liveHrefTag)
        const names = myCheerio.getContentByTagClass(html, tagClasses.competitionName)

        liveUrl[dayItem] = {
            url: hrefs,
            names: names,
            len: hrefs.length,
        }
    }

    console.log('结束爬去直播间的url!')
    
    return liveUrl
}

/**
 * 重构data
 */
function reconstructData (data) {
    
    for(const item in data) {
        const newurl = data[item].url.map(urlItem => {
            return 'https:' + urlItem.slice(0, urlItem.indexOf('/tab')) + '/tab/' + api.API_LIVE_SUFFIEX
        })
        data[item].url = newurl
        
    }

    return data
}

/**
 * 获取直播间人数
 */
async function getLivePeople (data) {
    for(const item in data) {
        const peopleCounts = []
        const promises = []
        for (const urlItem of data[item].url) {
            const peopleCount = await myPuppeteer.runPuppeteerScript(urlItem, tagClasses.peopleTag)
            peopleCounts.push(peopleCount)
        }

        data[item].peopleCounts = peopleCounts
    }
    return data
}


async function reptile() {
    const data = await getLivePeople(reconstructData(await getDatePage()))
    return data
}



module.exports = {
    reptile
}
