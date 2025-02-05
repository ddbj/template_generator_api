import json

def create_qualifier(qualifier_key: str, value: str|list) -> list[list[str]]:
    ret = []
    if isinstance(value, list):  # For array data
        for v in value:
            ret.append(["", "", "", qualifier_key, v])
    else:  # For string
        ret.append(["", "", "", qualifier_key, value])
    return ret

def create_feature(feature_name: str, feature_values: dict|list) -> list[list[str]]:
    ret = []
    if isinstance(feature_values, list):  # For array data (REFERENCE and COMMENT)
        for v in feature_values:
            ret.extend(create_feature(feature_name, v))
    else:
        for qualifier_key, value in feature_values.items():
            ret.extend(create_qualifier(qualifier_key, value))
    if ret:
        ret[0][1] = feature_name
    return ret

def create_common(common_json: dict) -> list[list[str]]:
    ret = []
    for feature_name, feature_values in common_json.items():
        if feature_name != "trad_submission_category":
            ret.extend(create_feature(feature_name, feature_values))
    if ret:
        ret[0][0] = "COMMON"
    return ret

if __name__ == "__main__":
    import sys
    input_json = sys.argv[1]

    with open(input_json, "r") as f:
        common_json = json.load(open(input_json, "r"))
    common = create_common(common_json)

    for row in common:
        row = map(str, row)
        print("\t".join(row))

