
/**
 * 1.1万人 --> 11000
 * 7038人 --> 7038
 * @param {String} countString 
 * @returns {Number}
 */
function convertToNumber(countString) {
    if (countString.includes("万")) {
        const numberPart = parseFloat(countString.replace("万人", ""));
        return numberPart * 10000;
    } else {
        return parseInt(countString.replace("人", ""))
    }
}

function convertComToNumber(countString) {
    if (countString.includes('场')) {
        const numberPart = parseInt(countString.replace("场", ""))
        return numberPart
    } else {
        return parseInt(countString)
    }
}

module.exports = {
    convertToNumber,
    convertComToNumber
}