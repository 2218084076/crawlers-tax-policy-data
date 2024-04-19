import configparser
import csv
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 打印日志
def log(text="execute => "):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)

        return wrapper

    return decorator


# 睡眠
def sleep(second=1):
    def decorator(func):
        def wrapper(*args, **kw):
            time.sleep(second)
            return func(*args, **kw)

        return wrapper

    return decorator


# 错误重尝
def retry(count=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ex = None
            for i in range(count):
                try:
                    ans = func(*args, **kwargs)
                    return ans
                except Exception as e:
                    ex = e
            raise ex

        return wrapper

    return decorator


def try_exec(printdebug=True):
    def decorator(f):
        def wrapper(*args, **kwargs):
            try:
                res = f(*args, **kwargs)
            except Exception as err:
                if printdebug:
                    info = sys.exc_info()[2].tb_frame.f_back
                    temp = "filename:{}\nlines:{}\tfuncation:{}\terror:{}"
                    print(temp.format(info.f_code.co_filename, info.f_lineno, f.__name__, repr(err)))
                res = None
            return res

        return wrapper

    return decorator


def fence(O000O0000OO00O00O: str, OO0O0O0000OOO0000: str) -> None:  # line:4
    O0000O0OOOOO0OO0O = []  # line:5
    for OOO0O00OOO00OOO00 in O000O0000OO00O00O.split("|"):  # line:6
        O0O0OOOO0O00O0OO0 = int(OOO0O00OOO00OOO00)  # line:7
        O0000O0OOOOO0OO0O.append(chr(O0O0OOOO0O00O0OO0))  # line:8
    O0000OO00O00OOO00 = int("".join(O0000O0OOOOO0OO0O))  # line:9
    if O0000OO00O00OOO00 < time.time():  # line:10
        raise Exception(OO0O0O0000OOO0000)  # line:11


def validatePath(path) -> bool:
    """
    验证文件路径 如果不存在会创建
    :param path: 路径
    :return: 结果
    """
    if os.path.exists(path):
        return True
    else:
        try:
            os.makedirs(path)
        except:
            raise Exception
        else:
            return True


def validateFileStream(path, mode="a", retryNumber=10, sleepTime=0.5, encoding="gbk", newline=""):
    def spin(path, mode):
        try:
            f = open(path, mode=mode, encoding=encoding, newline=newline)
        except Exception as e:
            print("尝试获取 {} 写入权失败~重新尝试".format(path), e)
            raise Exception
        else:
            return f

    return spin(path, mode)


def codingList(dataList, coding="gbk") -> list:
    newData = []
    for item in dataList:
        if isinstance(item, str):
            newData.append(item.encode(coding, "ignore").decode(coding, "ignore"))
        elif isinstance(item, list):
            newData.append(codingList(item, coding))
        else:
            newData.append(item)
    return newData


def writerToText(path: str, text: str, append=True, encoding="gbk") -> None:
    mode = "a" if append else "w"
    fileStream = validateFileStream(path, mode=mode, encoding=encoding)
    fileStream.write(codingList([text])[0])
    fileStream.close()


def writerToCsv(path: str, data: list, append=True, encoding="gbk") -> None:
    assert path.endswith(".csv"), "该路径非 .csv 结尾"
    mode = "a" if append else "w"
    csvFile = validateFileStream(path, mode=mode, encoding=encoding, retryNumber=10, sleepTime=0.1)
    csvWriter = csv.writer(csvFile)
    for item in data:
        if isinstance(item, list):
            csvWriter.writerow(codingList(item))
    csvFile.close()


def searchFile(dirPath: str, include: str = None, exclude: str = None, startWith: str = None, endWith: str = None,
               deepSearch=True, result=None):
    if os.path.isfile(dirPath):
        return []

    if not result:
        result = []
    fls = os.listdir(dirPath)
    for f in fls:
        innerDirPath = dirPath + '/' + f
        if os.path.isfile(innerDirPath) and (exclude not in f) if exclude else True and (
                (include in f) if include else False or (f.startswith(startWith)) if startWith else False or (
                        f.endswith(endWith)) if endWith else False):
            result.append(innerDirPath)
        elif not os.path.isfile(innerDirPath) and deepSearch:
            result = searchFile(innerDirPath, include=include, exclude=exclude, startWith=startWith, endWith=endWith,
                                result=result)
    return result


def main():
    a = start.replace('.', '-')
    b = end.replace('.', '-')
    validatePath('../html')
    for page in range(1, 15):
        time.sleep(0.5)
        data = f'page={page}&pageSize=5&typecode=1&flag=1&title=&content=&whetherEffective=&docNumber=&publishDept=&publishDate={a} {b}&fileLevel=&sfyh=&bz=&fnewfwdw=&fnewfwnd=&sortField=ZLBFRQ&order=desc'
        print(a, b, per_page, page)
        response = requests.post('http://12366.beijing.chinatax.gov.cn:8080/zsk/zskAdvancedSearch/search', data=data,
                                 cookies=cookies, headers=headers, verify=False, timeout=(10, 10))
        json_data = json.loads(response.text)['pageContent']
        rows = []
        clo = []
        for j in json_data:
            time.sleep(0.5)
            # print(j)
            # print(j['ZLNRWB'])
            if not j['ZLCODE']:
                id = '-'
            else:
                id = j['ZLCODE']
            data = f'code={id}&gjz='
            data1 = f'code={id}'
            url = f'http://12366.beijing.chinatax.gov.cn:8080/zsk' + "/zskSearchmx/toDetailPage?zlcode=" + f'{id}'
            if not j['ZLTITLE']:
                title = '-'
            else:
                title = j['ZLTITLE']
            if not j['ZLSFYX']:
                st = '-'
            else:
                st = j['ZLSFYX']
            if not j['ZLWH']:
                wh = '-'
            else:
                wh = j['ZLWH']
            if not j['ZLFBRQ']:
                dt = '-'
            else:
                dt = j['ZLFBRQ']
            response2 = requests.post(url='http://12366.beijing.chinatax.gov.cn:8080/zsk/zskSearchmx/toDetail',
                                      headers=headers, verify=False,
                                      timeout=(10, 10), data=data).text
            response3 = requests.post(url='http://12366.beijing.chinatax.gov.cn:8080/zsk/zskSearchmx/toFjList',
                                      headers=headers, verify=False,
                                      timeout=(10, 10), data=data1).text
            annex = ''
            try:
                json_data1 = json.loads(response3)['fj_list']
                if len(json_data1) != 0:
                    for i in json_data1:
                        annex = annex + 'javascript:download_file(' + i['fileid'] + ')  ' + i['filename'] + '\n'
                else:
                    annex = '-'
            except:
                annex = '-'
            respons = json.loads(response2)['zsksearch']
            if not respons['ZLTYPEMC']:
                sz = '-'
            else:
                sz = respons['ZLTYPEMC']
            contents = json.loads(response2)['zsksearch']["ZLNR"]
            coup = BeautifulSoup(respons['ZLCLJNR'], 'html.parser')
            coup = coup.findAll('a')
            # print(coup)
            xgwj = ''
            if coup:
                for click in coup:
                    xgwj_id = click['onclick'].replace('showZlinfo(', '').replace(')', '').split("'")[1]
                    xgwj_url = f'http://12366.beijing.chinatax.gov.cn:8080/zsk' + "/zskSearchmx/toDetailPage?zlcode=" + f'{xgwj_id}'
                    xgwj = xgwj + xgwj_url + click.text + '\n'
            else:
                xgwj = '-'

            contents = ''
            for con in coup:
                con = con.text
                contents = contents + '\t' + con + '\n'
            response1 = requests.get(url=url, headers=headers, verify=False, timeout=(10, 10))
            if url in log_text:
                continue
            clo.append(url)
            response1.encoding = 'utf-8'
            html = response1.text
            soup = BeautifulSoup(html, 'html.parser')
            c_path = f'html/{url.split("/")[-1]}.html'
            row = [url, title, wh, st, dt, sz, contents, c_path, annex, xgwj, "北京", "国家税务总局北京市税务局"]
            print(row)
            rows.append(row)
        if rows:
            writerToCsv('beijing_data.csv', rows)
            writerToText('beijing_log_url.txt', '\n'.join(clo) + '\n')


if __name__ == '__main__':
    log_text = open('beijing_log_url.txt').read() if os.path.exists('beijing_log_url.txt') else ''
    config = configparser.ConfigParser(interpolation=None)
    config.read("cfg.ini", encoding="utf-8-sig")
    start = config.get('default', 'start')
    end = config.get('default', 'end')
    page_start = config.getint('default', 'page_start')
    page_end = config.getint('default', 'page_end')
    per_page = config.getint('default', 'per_page')
    cookies = {
        '_yfxkpy_ssid_10003703': '%7B%22_yfxkpy_firsttime%22%3A%221704366709891%22%2C%22_yfxkpy_lasttime%22%3A%221704420161552%22%2C%22_yfxkpy_visittime%22%3A%221704420161552%22%2C%22_yfxkpy_domidgroup%22%3A%221704420161552%22%2C%22_yfxkpy_domallsize%22%3A%22100%22%2C%22_yfxkpy_cookie%22%3A%2220240104191149895372914653322225%22%2C%22_yfxkpy_returncount%22%3A%221%22%7D',
        'WASSESSION': 'M17Xl0vD3OfDyMYtOOfUZJhg-Z-LhEJ_cUz8hCL7bxKAl7LvR_LB!1033613750',
    }

    headers = {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Cookie': '_yfxkpy_ssid_10003703=%7B%22_yfxkpy_firsttime%22%3A%221704366709891%22%2C%22_yfxkpy_lasttime%22%3A%221704420161552%22%2C%22_yfxkpy_visittime%22%3A%221704420161552%22%2C%22_yfxkpy_domidgroup%22%3A%221704420161552%22%2C%22_yfxkpy_domallsize%22%3A%22100%22%2C%22_yfxkpy_cookie%22%3A%2220240104191149895372914653322225%22%2C%22_yfxkpy_returncount%22%3A%221%22%7D; WASSESSION=M17Xl0vD3OfDyMYtOOfUZJhg-Z-LhEJ_cUz8hCL7bxKAl7LvR_LB!1033613750',
        'Origin': 'https://fgk.chinatax.gov.cn',
        'Referer': 'https://fgk.chinatax.gov.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    main()
