import time, sys, os, re, csv
import requests
import configparser
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import json
import datetime

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


import time


def get_timestamp_from_formattime(format_time):
    struct_time = time.strptime(format_time, '%Y-%m-%d %H:%M:%S')
    return time.mktime(struct_time)


def main():
    validatePath('html')
    a = start.replace('.', '-') + ' 00:00:00'
    b = end.replace('.', '-') + ' 23:59:59'
    a_time = get_timestamp_from_formattime(a)
    b_time = get_timestamp_from_formattime(b)
    break_flag = 0
    flag = 1
    rows = []
    clo = []
    last_coup = []
    for page in range(1, 10):
        print(start, end, per_page, page)
        print(flag)
        if break_flag == 1:
            break
        if flag == 1:
            url = "https://guangdong.chinatax.gov.cn/siteapps/webpage/gdtax/fgk/ssfgk/policy_list.jsp"
            data = f'pageNo={page}&pageSize=20&display=none&taxType=&channelId=40b75ee10aa84d5fbe9ea5c9ca4df1ef&showItem=localTaxPolicy&parentId=&openStatus=localTaxOpen&title=&wordType=&beginDate=&endDate=&yearType=&contentKey=&publishOrg=&pagination_input=1'
            response = requests.post(url=url, headers=headers, data=data, timeout=(3, 3))
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser').find('div', {'class': 'ssfgk-result-list'})
            coup = soup.findAll('li', {'class': 'clearfix'})
            if coup == last_coup:
                break
            last_coup = coup
            flag = 0
            for c in coup:
                try:
                    flag = 1
                    dt = c.find('span', {'class': 'fwrq'}).text
                    dt1 = dt + ' 00:00:00'
                    dt_time = get_timestamp_from_formattime(dt1)
                except:
                    dt_time = '2050-01-01 00:00:00'
                    dt_time = get_timestamp_from_formattime(dt_time)
                    print('-------------------break2----------------------')
                try:
                    title = c.find('a').text
                except:
                    title = '-'
                try:
                    wh = c.find('span', {'class': 'fwh'}).text
                except:
                    wh = '-'
                if wh == '':
                    wh = '-'

                if int(dt_time) >= int(a_time) and int(dt_time) <= int(b_time):
                    url = 'https://guangdong.chinatax.gov.cn' + c.find('a')['href']
                    print(url)
                    c_path = f'html/{url.split("/")[-1]}'
                    if url in log_text:
                        continue
                    clo.append(url)
                    response1 = requests.get(url=url, headers=headers, timeout=(3, 3))
                    response1.encoding = 'utf-8'
                    soup1 = BeautifulSoup(response1.text, 'html.parser')
                    coup1 = soup1.find('div', {'class': 'meta_main'})
                    try:
                        st = coup1.find('span', {'class': 'yxx'}).text
                    except:
                        st = '-'
                    content = ''
                    xgwj = ''
                    annex = ''
                    coup1 = soup1.find('div', {'class': 'content'}).findAll('p')
                    for c1 in coup1:
                        content = content + '\t' + '\n' + c1.text
                    try:
                        annexs = soup1.find('div', {'class': 'rel_news relAtt clearfix'}).find_all('a')
                        for an in annexs:
                            if an.text != '':
                                my_url = 'https://guangdong.chinatax.gov.cn/' + url.split("/")[-5] + '/' + \
                                         url.split("/")[-4] + '/' + url.split("/")[-3] + '/' + url.split("/")[-2]
                                annex_url = my_url + an['href']
                                annex_name = an.text
                                annex = annex + annex_url + '  ' + annex_name + '\n'
                    except:
                        annexs = '-'
                    try:
                        xgwjs = soup1.find('div', {'class': 'rel_news xgjd clearfix'}).findAll('a')
                        xgwj2s = soup1.find('div', {'class': 'rel_news xgwj clearfix'}).findAll('a')
                        for x in xgwjs:
                            if x.text != '':
                                xgwj_url = 'https://guangdong.chinatax.gov.cn' + x['href']
                                xgwj_name = x.text
                                xgwj = xgwj + xgwj_url + '  ' + xgwj_name + '\n'
                        for x2 in xgwj2s:
                            if x2.text != '':
                                xgwj_url2 = 'https://guangdong.chinatax.gov.cn' + x2['href']
                                xgwj_name2 = x2.text
                                xgwj = xgwj + xgwj_url2 + '  ' + xgwj_name2 + '\n'
                    except:
                        xgwj = '-'
                    if xgwj == '':
                        xgwj = '-'
                    if annex == '':
                        annex = '-'
                    sz = '-'
                    row = [url, title, wh, st, dt, sz, content, c_path, annex, xgwj, "广东", "国家税务总局广东省税务局"]
                    # print(row)
                    rows.append(row)
                elif int(dt_time) > int(b_time):
                    pass
                elif int(dt_time) < int(a_time):
                    break_flag = 1
                    break
                else:
                    pass
        else:
            break
    if rows:
        writerToCsv('guangdong_data.csv', rows)
        writerToText('guangdong_log_url.txt', '\n'.join(clo) + '\n')


if __name__ == '__main__':
    log_text = open('guangdong_log_url.txt').read() if os.path.exists('guangdong_log_url.txt') else ''
    config = configparser.ConfigParser(interpolation=None)
    config.read("cfg.ini", encoding="utf-8-sig")
    start = config.get('default', 'start')
    end = config.get('default', 'end')
    page_start = config.getint('default', 'page_start')
    page_end = config.getint('default', 'page_end')
    per_page = config.getint('default', 'per_page')

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    main()
