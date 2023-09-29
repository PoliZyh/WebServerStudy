/**
 * * author: @Ethan_Zhang
 * * githun: https://github.com/PoliZyh
 * * date: 2023/9/29
 */

/**
 * * 实现思路：
 * * 再爬去每日赛程界面，每日赛程界面的url变化的只有最后一级，比如2023-09-20或者2023-09-21(需要对date处理)
 * * 再爬去改界面下.wa-olympic-schedule-list-item类下的a标签身上的href属性，因为改属性指向直播间的界面
 * * 在前往直播间界面之前，需要将href的最后一级由数据改为聊天室(这么做之后聊天室标签上才会显示直播间人数)
 * * 最后爬去.text-position-talkroom标签中的Text文本即可爬到直播间人数
 * * 通过fs模块导出数据
 */

const server = require('./server/index.js')
const reptile = require('./reptile.js')

// 开启服务器
server.createServer();


(async () => {
    console.log(await reptile.reptile())
})()





