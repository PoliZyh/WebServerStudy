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
        else console.log('文件写入成功')
    })
}

module.exports = {
    outputDataToJSON
}