const fs = require('fs')
const path = require('path')
const day = require('./day')

function outputDataToJSON(data) {
    const jsonData = JSON.stringify(data, null, 2)
    const mkPath = path.join(__dirname, '../../outputs', `统计于${day.today()}`)

    fs.mkdirSync(mkPath)

    const fileName = 'output.json'

    fs.writeFile(path.join(mkPath, fileName), jsonData, (err) => {
        if (err) console.log('文件写入出错')
        else console.log('all文件写入成功')
    })

    outputDataToJSONBriefly(data, mkPath)
}

function outputDataToJSONBriefly(data, mkPath) {
    let res = []
    let index = 1
    for (const key in data) {
        const str = `${index}. ${key} ${data[key].mostPopular[0].name} ${data[key].mostPopular[0].count}`
        index ++
        res.push(str)
    }
    const jsonData = JSON.stringify(res, null, 2)
    const fileName = 'outputBriefly.json'
    fs.writeFile(path.join(mkPath, fileName), jsonData, (err) => {
        if (err) console.log('文件写入出错')
        else console.log('briefly文件写入成功')
    })
}

module.exports = {
    outputDataToJSON
}