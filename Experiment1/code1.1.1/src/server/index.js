const express = require('express')
const mySchedule = require('../utils/schedule')

const app = express()



function createServer() {
    // 开启端口
    app.listen(3000, () => {
        console.log('server is running at http://127.0.0.1:3000')
        
    })

    // 开启爬虫任务
    mySchedule.startReptileSchedule()
    

}



module.exports = {
    createServer
}