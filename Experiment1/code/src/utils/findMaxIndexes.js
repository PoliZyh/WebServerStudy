/**
 * 获取所有最大值的索引
 * @param {Array} arr 
 * @returns {Array} indexes
 */
function findMaxIndexes(arr) {
    if (arr.length === 0) {
        return [];
    }

    let maxIndexes = [];
    let maxVal = -10000;

    for (let i = 0; i < arr.length; i++) {
        if (maxVal < arr[i]) maxVal = arr[i]
    }

    for (let i = 0; i < arr.length; i++) {
        if (maxVal === arr[i]) maxIndexes.push(i)
    }

    return maxIndexes;
}


module.exports = findMaxIndexes