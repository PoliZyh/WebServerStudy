const server = require('./server')
const reptile = require('./reptile')

// 开启服务器
server.createServer();

(async () => {
    console.log(await reptile())
})()
