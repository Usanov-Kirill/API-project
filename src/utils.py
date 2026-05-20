import json


def dict_list_to_json(dict_list, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dict_list, f, ensure_ascii=False, indent=2)


def json_to_dict_list(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
