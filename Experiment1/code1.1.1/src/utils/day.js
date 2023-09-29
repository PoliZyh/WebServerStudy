

function getAllDateArray() {
    const oldDay = new Date('2023-09-19')
    const today = new Date()
    const resArr = []

    while(oldDay <= today) {
        // 将当前日期添加到数组
        resArr.push(oldDay.toISOString().split('T')[0]);
        oldDay.setDate(oldDay.getDate() + 1)
    }

    return resArr
}

function today() {
    const currentDate = new Date();

    const year = currentDate.getFullYear(); // 年份
    const month = currentDate.getMonth() + 1; // 月份（注意：月份从0开始，所以要加1）
    const day = currentDate.getDate(); // 日期
    const hours = currentDate.getHours(); // 小时
    const minutes = currentDate.getMinutes(); // 分钟
    const seconds = currentDate.getSeconds(); // 秒钟


    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

module.exports = {
    getAllDateArray,
    today
}