
const api = require('./api/setting')
const day = require('./utils/day.js')
const myPuppeteer = require('./utils/puppeteer.js')
const myCheerio = require('./utils/cheerio')
const getHTML = require('./utils/getHTML')
const tagClasses = require('./tagClasses')
const convertToNumber = require('./utils/convertToNumber')
const findMaxIndexes = require('./utils/findMaxIndexes')
const output = require('./utils/file-output')

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

    for (const dayItem of dateArr) {
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
    
    for (const item in data) {
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
    for (const item in data) {
        const peopleCounts = []
        // const promises = []
        for (const urlItem of data[item].url) {
            // * 此处做了性能优化
            const peopleCount = await myPuppeteer.runPuppeteerScript(urlItem, tagClasses.peopleTag)
            peopleCounts.push(peopleCount)
        }

        data[item].peopleCounts = peopleCounts
    }
    return data
}

/**
 * 修正peopleCounts
 * @returns 
 */
function reconstructDataForPeople(data) {
    for (const item in data) {
        const pCounts = data[item].peopleCounts
        const pStr = pCounts.join(" ") 
        const regexPeople = /\((.*?)\)/g // 匹配括号内的内容
        const matchPeople = []
        let match
        while ((match = regexPeople.exec(pStr)) !== null) {
            matchPeople.push(match[1]);
        }
        data[item].peopleCounts = matchPeople
    }
    return data
}

/**
 * 获取输出的data内容
 * @param {Array} data 
 */
function getOutputData(data) {
    const res = {}

    for (const item in data) {
        const objItem = {}

        objItem.date = '比赛的日期为:' + item
        objItem.mostPopular = []

        data[item].mostIndexes.map(index => {
            const liveObj = {
                'title': '人气王之一!',
                'name': data[item].names[index],
                'count': '人数为' + data[item].peopleCounts[index]
            }
            objItem.mostPopular.push(liveObj)
        })

        res[item] = objItem
    }

    return res
}


async function reptile() {
    let data = reconstructDataForPeople(await getLivePeople(reconstructData(await getDatePage())))

    // 获取索引
    for (const item in data) {
        // 字符串to数值
        const numberCount = data[item].peopleCounts.map(count => {
            return convertToNumber(count)
        })
        const mostIndexes = findMaxIndexes(numberCount)
        data[item].mostIndexes = mostIndexes
    }

    // 格式化data
    data = getOutputData(data)

    // 输出
    output.outputDataToJSON(data)

    return data
}



module.exports = {
    reptile
}
