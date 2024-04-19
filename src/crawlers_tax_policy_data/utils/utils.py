from datetime import datetime


def date_obj(date_str: str):
    """
    Convert the date string to a datetime object
    :param date_str:
    :return:
    """
    date_object = datetime.strptime(date_str, "%Y%m%d")
    return date_object


def parse_timestamp(timestamp:str):
    """
    Convert the timestamp string to a datetime object
    :param timestamp:
    :return:
    """
    date_time = datetime.fromtimestamp(timestamp)

