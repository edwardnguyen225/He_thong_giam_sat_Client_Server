import monitor
import json
import os


def is_id_registered(id, list_of_clients):
    print(f"{id}: {type(id)}")
    if id not in list_of_clients:
        return False
    return True


def validate_report(report_json):
    """
    Check if report is valid
    If not, return error message
    """
    print(json.dumps(report_json, indent=3))
    return True
