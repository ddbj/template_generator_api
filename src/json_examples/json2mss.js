const fs = require('fs');

function createQualifier(qualifierKey, value) {
    const ret = [];
    if (Array.isArray(value)) { // For array data
        for (const v of value) {
            ret.push(["", "", "", qualifierKey, v]);
        }
    } else { // For string
        ret.push(["", "", "", qualifierKey, value]);
    }
    return ret;
}

function createFeature(featureName, featureValues) {
    let ret = [];
    if (Array.isArray(featureValues)) { // For array data (REFERENCE and COMMENT)
        for (const v of featureValues) {
            ret = ret.concat(createFeature(featureName, v));
        }
    } else {
        for (const qualifierKey in featureValues) {
            if (featureValues.hasOwnProperty(qualifierKey)) {
                const value = featureValues[qualifierKey];
                ret = ret.concat(createQualifier(qualifierKey, value));
            }
        }
    }
    if (ret.length > 0) {
        ret[0][1] = featureName;
    }
    return ret;
}

function createCommon(commonJson) {
    let ret = [];
    for (const featureName in commonJson) {
        if (commonJson.hasOwnProperty(featureName) && !featureName.startsWith("_")) {
            const featureValues = commonJson[featureName];
            ret = ret.concat(createFeature(featureName, featureValues));
        }
    }
    if (ret.length > 0) {
        ret[0][0] = "COMMON";
    }
    return ret;
}

// main
const args = process.argv.slice(2);
if (args.length === 0) {
    console.error("Please provide the path to the JSON file as an argument.");
    process.exit(1);
}

const inputJson = args[0];

fs.readFile(inputJson, 'utf8', (err, data) => {
    if (err) {
        console.error("Error reading file:", err);
        return;
    }
    const commonJson = JSON.parse(data);
    const common = createCommon(commonJson);

    common.forEach(row => {
        console.log(row.map(String).join("\t"));
    });
});
