import json
import datetime
import copy
import socket

ERROR_VALUE = "ValueError"
ERROR_NOT_ENOUGH_KEYS = "MissingKeyError"

TYPE_DATETIME = "datetime"
TYPE_SIZE = "size"
TYPE_FREQUENCY = "frequency"
TYPE_INT = "integer"
TYPE_FLOAT = "float"

REPORT_LAYOUT = {
    TYPE_DATETIME: {
        "Boot time": TYPE_DATETIME,
        "CPU info": {
            "Physical cores": TYPE_INT,
            "Total threads": TYPE_INT,
            "Max Frequency": TYPE_FREQUENCY,
            "Min Frequency": TYPE_FREQUENCY,
            "Current Frequency": TYPE_FREQUENCY
        },
        "Memory usage": {
            "Total": TYPE_SIZE,
            "Available": TYPE_SIZE,
            "Used": TYPE_SIZE,
            "Percentage": TYPE_FLOAT
        }
    }
}


def is_id_registered(id, list_of_clients):
    if id not in list_of_clients:
        return False
    return True


def is_name_correct(name, id, list_of_clients):
    # try catch is to prevent id not exist
    try:
        return name == list_of_clients[id]["name"]
    except:
        return False


def does_mac_address_exist(mac_address, list_of_clients):
    mac_address_key = "MAC Address"
    for client_info in list(list_of_clients.values()):
        tmp = client_info[mac_address_key]
        print(f"{mac_address} ? {tmp}")
        if mac_address == client_info[mac_address_key]:
            return True
    return False


def get_report_error(report_json):
    """
    Check if report has any error
    If not, return error message
    Else return None
    """
    # print(json.dumps(report_json, indent=3))
    errors = {
        ERROR_NOT_ENOUGH_KEYS: [],
        ERROR_VALUE: []
    }
    try:
        datetime_str = list(report_json.keys())[0]
        validate_format(datetime_str, TYPE_DATETIME,
                        errors, "Report timestamp")
    except:
        return "No report timestamp"

    report_inner = report_json[datetime_str]
    validate_dict(report_inner, REPORT_LAYOUT[TYPE_DATETIME], errors)

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

        full_key = key if not parent_key else parent_key + "/" + key

        if type(template[key]) is dict:
            if type(value) is dict:
                inner_dict = curr_dict[key]
                inner_template = template[key]
                validate_dict(inner_dict, inner_template, errors, key)
                continue
            else:
                errors[ERROR_VALUE].append(full_key + "!=" + "dict")

        # print(f"Checking {key}, {value} is {template[key]}")
        validate_format(value, template[key], errors, full_key)


def validate_dict_keys(curr_dict, template, errors, parent_key=None):
    for template_key in template.keys():
        if template_key not in curr_dict.keys():
            missing_key = template_key if not parent_key else parent_key + "/" + template_key
            errors[ERROR_NOT_ENOUGH_KEYS].append(missing_key)


def validate_format(value, format, errors, key_path):
    if format == TYPE_DATETIME and not is_datetime(value):
        errors[ERROR_VALUE].append(key_path + "!=" + TYPE_DATETIME)
    elif format == TYPE_SIZE and not is_storage_size(value):
        errors[ERROR_VALUE].append(key_path + "!=" + TYPE_SIZE)
    elif format == TYPE_FREQUENCY and not is_frequency(value):
        errors[ERROR_VALUE].append(key_path + "!=" + TYPE_FREQUENCY)
    elif format == TYPE_FLOAT and type(value) is not float:
        errors[ERROR_VALUE].append(key_path + "!=" + TYPE_FLOAT)
    elif format == TYPE_INT and type(value) is not int:
        errors[ERROR_VALUE].append(key_path + "!=" + TYPE_INT)


def is_datetime(datetime_str):
    try:
        datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
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


def is_frequency(str):
    tmp_str = copy.deepcopy(str)
    unit = "Mhz"
    tmp_str = tmp_str.replace(unit, "")
    try:
        fr = float(tmp_str)
    except ValueError:
        return False
    return True


def is_IP(str):
    try:
        socket.inet_aton(str)
    except socket.error:
        return False
    return True


def main():
    msg = """
    {
        "2021-04-29 10:26:14.684033": {
            "Boot time": "2021-04-28 10:30:44.926089",
            "CPU info": {
                "Physical cores": 4,
                "Total threads": 8,
                "Max Frequency": "1896.00Mhz",
                "Min Frequency": "0.00Mhz",
                "Current Frequency": "1696.00Mhz"
            },
            "Memory usage": {
                "Total": "15.88GB",
                "Available": "5.33GB",
                "Used": "10.55GB",
                "Percentage": 66.4
            }
        }
    }
    """
    report = json.loads(msg)
    errors = get_report_error(report)
    if errors:
        print(errors)
    else:
        print("Report valid")


if __name__ == "__main__":
    main()
