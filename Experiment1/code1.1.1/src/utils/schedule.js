const schedule = require('node-schedule')
const SETTING = require('../setting')
const reptile = require('../reptile')

function startReptileSchedule() {
    const rule = new schedule.RecurrenceRule()
    rule.hour = SETTING.repiteTime.hour
    rule.minute = SETTING.repiteTime.min

    const job = schedule.scheduleJob("reptile" ,rule, async () => {
        try {
            await reptile()
            console.log('爬取任务已完成')
        } catch (error) {
            console.error('爬取任务出错:', error)
        }
    })
}

module.exports = {
    startReptileSchedule
}