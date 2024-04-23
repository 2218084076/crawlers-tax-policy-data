import re
from datetime import datetime


def date_obj(date_str: str):
    """
    Convert the date string to a datetime object
    :param date_str:
    :return:
    """
    date_object = datetime.strptime(date_str, "%Y%m%d")
    return date_object


def parse_timestamp(timestamp):
    """
    Convert the timestamp string to a datetime object
    :param timestamp:
    :return:
    """
    date_time = datetime.fromtimestamp(timestamp)


def clean_text(text):
    """
    Used to clean and standardize extracted text
    :param text:
    :return:
    """
    text = re.sub(r'[\xa0\u3000\n\t]+', ' ', text)
    return text.strip()
