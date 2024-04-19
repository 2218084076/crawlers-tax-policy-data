import time, sys, os, re, csv
import requests
import configparser
from bs4 import BeautifulSoup
import urllib3

# from requests.packages.urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def sleep(second=1):
    def decorator(func):
        def wrapper(*args, **kw):
            time.sleep(second)
            return func(*args, **kw)

        return wrapper

    return decorator


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


def main():
    validatePath('html')
    for page in range(page_start, page_end):
        print(start, end, per_page, page)
        data = f"channelid=123952&searchword=&extrasql=PRINTTIME%3E%3D'{start}'+and+PRINTTIME%3C%3D'{end}'&page={page}&prepage={per_page}"
        response = requests.post('https://shanghai.chinatax.gov.cn/was5/web/search', cookies=cookies, headers=headers,
                                 data=data)
        xml = response.text
        reg = re.compile('<URL><!\[CDATA\[(.*?)]]></URL>').findall(xml)
        if not reg:
            break
        rows = []
        clo = []
        for item in reg:
            url = 'https://shanghai.chinatax.gov.cn' + item
            print(url)
            # url = 'https://shanghai.chinatax.gov.cn/zcfw/zcfgk/zhsszc/202312/t469904.html'
            clo.append(url)
            response = requests.get(url, cookies=cookies, headers=headers)
            response.encoding = 'utf-8'
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.get_text().strip()
            _ = soup.find('span', attrs={'id': 'ivs_date'})
            announcement_date = _.get_text().strip() if _ else '-'

            _ = soup.find('div', attrs={'id': 'content'})
            content = _.get_text().strip() if _ else '-'
            content_html = str(_) if _ else '-'
            c_path = f'html/{url.split("/")[-1]}'
            writerToText(c_path, content_html)

            _ = soup.find('meta', attrs={'name': 'ColumnName'})
            type_of_tax = _['content'].strip() if _ else '-'

            reg = re.compile('<div>文号：(.*?)</div>').findall(html)
            circular_coding = reg[0] if reg else '-'

            reg = re.compile('<p>状态：(.*?)</p>').findall(html)
            effectiveness = reg[0] if reg else '-'
            reg = re.compile('var fileName=\'(.*?)\'').findall(html)
            if reg:
                p = url.replace(url.split('/')[-1], '')
                reg = re.compile('\./(.*?)">(.*?)</a>').findall(reg[0])
                annex_lst = []
                for h, t in reg:
                    link = p + h
                    line = link + ' ' + t
                    annex_lst.append(line)
                annex = '\n'.join(annex_lst)
            else:
                annex = None
            if not annex:
                annex = '-'
            reg = re.compile('var rel = \'(.*?)\';').findall(html)
            if reg:
                tags = BeautifulSoup(reg[0], 'html.parser').find_all('a')
                xg = []
                for xg_tag in tags:
                    t = xg_tag.get_text().strip()
                    h = xg_tag['href'].replace('../../..', 'https://shanghai.chinatax.gov.cn/zcfw')
                    line = h + ' ' + t
                    xg.append(line)
                related_doc = '\n'.join(xg)
            else:
                related_doc = None
            if not related_doc:
                related_doc = '-'

            row = [url, title, circular_coding, effectiveness, announcement_date, type_of_tax, content, c_path, annex,
                   related_doc, "上海", "国家税务总局上海市税务局"]
            print(row)
            rows.append(row)
        if rows:
            writerToCsv('shanghai_data.csv', rows)


if __name__ == '__main__':
    log_text = open('shanghai_log_url.txt').read() if os.path.exists('shanghai_log_url.txt') else ''
    config = configparser.ConfigParser(interpolation=None)
    config.read("cfg.ini", encoding="utf-8-sig")
    start = config.get('default', 'start')
    end = config.get('default', 'end')
    page_start = config.getint('default', 'page_start')
    page_end = config.getint('default', 'page_end')
    per_page = config.getint('default', 'per_page')
    # start = "2024.01.01"
    # end = "2024.02.26"
    # page_start = 1
    # page_end = 1000
    # per_page = 15
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
        'Origin': 'https://shanghai.chinatax.gov.cn',
        'Referer': 'https://shanghai.chinatax.gov.cn/zcfw/zcfgk/index_1.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    main()
