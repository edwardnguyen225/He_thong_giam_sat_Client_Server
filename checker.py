import json
import datetime
import copy

ERROR_VALUE = "ValueError"
ERROR_NOT_ENOUGH_KEYS = "MissingKeyError"

DATETIME = "datetime"
SIZE = "size"

REPORT_LAYOUT = {
    DATETIME: {
        "Boot time": DATETIME,
        "Memory usage": {
            "Total": SIZE,
            "Available": SIZE,
            "Used": SIZE,
            "Percentage": "float"
        }
    }
}


def is_id_registered(id, list_of_clients):
    if id not in list_of_clients:
        return False
    return True


def get_report_error(report_json):
    """
    Check if report has any error
    If not, return error message
    Else return None
    """
    # print(json.dumps(report_json, indent=3))
    errors = {
        ERROR_VALUE: [],
        ERROR_NOT_ENOUGH_KEYS: []
    }
    datetime_str = list(report_json.keys())[0]
    validate_format(datetime_str, DATETIME, errors, "Report timestamp")

    report_inner = report_json[datetime_str]
    validate_dict(report_inner, REPORT_LAYOUT[DATETIME], errors)

    errors_return = ""
    for error_type, error_content in errors.items():
        if errors[error_type]:
            errors_return += error_type + ": " + error_content[0]
            if len(error_content) > 1:
                for error in error_content[1:]:
                    errors_return += ", " + error

            errors_return += "; "

    return errors_return


def validate_dict(curr_dict, template, errors, parent_key=None):
    err_count_before = len(errors)
    # print(json.dumps(curr_dict, indent=3))
    validate_dict_keys(curr_dict, template, errors, parent_key)
    for key, value in curr_dict.items():
        if key not in template.keys():  # Is this line necessary?
            continue

        if type(value) is dict:
            inner_dict = curr_dict[key]
            inner_template = template[key]
            validate_dict(inner_dict, inner_template, errors, key)
        else:
            full_key = key if not parent_key else parent_key + "/" + key
            # print(f"Checking {key}, {value} is {template[key]}")
            validate_format(value, template[key], errors, full_key)


def validate_dict_keys(curr_dict, template, errors, parent_key=None):
    for template_key in template.keys():
        if template_key not in curr_dict.keys():
            missing_key = template_key if not parent_key else parent_key + "/" + template_key
            errors[ERROR_NOT_ENOUGH_KEYS].append(missing_key)


def validate_format(value, format, errors, key_path):
    if format == DATETIME and not is_datetime(value):
        errors[ERROR_VALUE].append(key_path + "!=" + DATETIME)
    elif format == SIZE and not is_storage_size(value):
        errors[ERROR_VALUE].append(key_path + "!=" + SIZE)
    elif format == "float" and type(value) is not float:
        errors[ERROR_VALUE].append(key_path + "!=" + "float")


def is_datetime(datetime_str):
    try:
        datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
    except:
        return False
    return True


def is_storage_size(str):
    tmp_str = copy.deepcopy(str)
    size_unit = ["B", "K", "M", "G", "T", "P"]
    if tmp_str[-1] != "B":
        return False
    tmp_str = tmp_str[:-1]
    if tmp_str[-1] in ["K", "M", "G", "T", "P"]:
        tmp_str = tmp_str[:-1]
    try:
        size = float(tmp_str)
    except ValueError:
        return False

    if size < 0.0:
        return False

    return True


def main():
    msg = """
        {
            "2021-04-26 09:19:01.214034": {
                "Boot time": "2021-04-25 10:17:54.214035",
                "Memory usage": {
                    "Total": "15.88GB",
                    "Available": "6.22GB",
                    "Used": "9.66GB",
                    "Percentage": 60.8
                }
            }
        }
    """
    report = json.loads(msg)
    errors = get_report_error(report)
    if errors:
        print(errors)


if __name__ == "__main__":
    main()
