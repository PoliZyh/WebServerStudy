

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



module.exports = {
    getAllDateArray
}