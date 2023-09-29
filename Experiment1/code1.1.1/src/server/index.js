const express = require('express')

const app = express()



function createServer() {
    // 开启端口
    app.listen(3000, () => {
        console.log('server is running at http://127.0.0.1:3000')
    })

}



module.exports = {
    createServer
}