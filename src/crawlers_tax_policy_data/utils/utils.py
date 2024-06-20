# -*- coding: utf-8 -*-
"""
utils
"""
import re
from datetime import datetime

pattern = r'^\S+〔\d+〕\d+号$'


def date_obj(date_str: str):
    """
    Convert the date string to a datetime object
    :param date_str:
    :return:
    """
    date_object = datetime.strptime(date_str, "%Y%m%d")
    return date_object


def clean_text(text):
    """
    Used to clean and standardize extracted text
    :param text:
    :return:
    """
    text = re.sub(r'[\u200b\u2004\u2002\u2003\xa0\u3000]+', lambda m: ' ' * len(m.group()), text)
    return text


def is_match(text):
    """
    Check if the text matches the pattern
    :param text:
    :return:
    """
    return bool(re.match(pattern, text))


def extract_url_base(url):
    """
    Extract the base url from the url
    :param url:
    :return:
    """
    parts = url.split('/')
    for i in range(len(parts)):
        if len(parts[i]) == 4 and parts[i].isdigit() and i + 3 < len(parts):
            if parts[i + 1].isdigit() and parts[i + 2].isdigit():
                return '/'.join(parts[:i + 3])
    return ''
