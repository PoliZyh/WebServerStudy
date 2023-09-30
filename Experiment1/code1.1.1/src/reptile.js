const api = require('./api')
const myPuppeteer = require('./utils/puppeteer')
const tagClasses = require('./tagClasses')
const convertToNumber = require('./methods/convertToNumber')
const findMaxIndexes = require('./methods/findMaxIndexes')
const output = require('./utils/file-output')

async function getAllHrefsAndText() {
    const res = await myPuppeteer.runPuppeteerScript(api.API_ROOT, tagClasses.liveHrefTag, tagClasses.totalCom, tagClasses.dateTag, tagClasses.competitionName)
    return res
}

function restructData(data) {

    const res = {}

    const gamesCount = data.dynamicContents.map(item => convertToNumber.convertComToNumber(item))

    let indexDate = 0
    let indexHrefs = 0
    gamesCount.forEach(item => {
        const date = data.dynamicDates[indexDate]
        const gameCount = data.dynamicContents[indexDate]
        indexDate++
        const url = data.dynamicHrefs.slice(indexHrefs, indexHrefs + item).map(urlItem => {
            return 'https:' + urlItem.slice(0, urlItem.indexOf('/tab')) + '/tab/' + api.API_LIVE_SUFFIEX
        })
        const names = data.dynamicNames.slice(indexHrefs, indexHrefs + item)
        indexHrefs += item
        const obj = {
            date,
            gameCount,
            url,
            names
        }
        res[date] = obj
    })

    return res
}

async function getLivePeople(data) {

    for (const item in data) {
        // const peoCounts = []
        // for (const urlItem of data[item].url) {
        //     const peoCount = await myPuppeteer.runPuppeteerScriptForTexts(urlItem, tagClasses.peopleTag) 
        //     peoCounts.push(peoCount)
        // }
        const peoCounts = await myPuppeteer.runPuppeteerScriptForTexts(data[item].url, tagClasses.peopleTag)
        data[item].peoCounts = peoCounts
    }

    return data
}


function reconstructDataForPeople(data) {
    for (const item in data) {
        const pCounts = data[item].peoCounts
        const pStr = pCounts.join(" ") 
        const regexPeople = /\((.*?)\)/g // 匹配括号内的内容
        const matchPeople = []
        let match
        while ((match = regexPeople.exec(pStr)) !== null) {
            matchPeople.push(match[1]);
        }
        data[item].peoCounts = matchPeople
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
                'count': '人数为' + data[item].peoCounts[index]
            }
            objItem.mostPopular.push(liveObj)
        })

        res[item] = objItem
    }

    return res
}


async function reptile() {
    let data = reconstructDataForPeople(await getLivePeople(restructData(await getAllHrefsAndText())))

    for (const item in data) {
        // 字符串to数值
        const numberCount = data[item].peoCounts.map(count => {
            return convertToNumber.convertToNumber(count)
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


module.exports = reptile