"""
` base url: http://sfcx.neimenggu.chinatax.gov.cn/ `

"""
import httpx
from lxml import etree

from crawlers_tax_policy_data.spider.base import BaseSpider


class NMG_Spider(BaseSpider):
    url = 'http://sfcx.neimenggu.chinatax.gov.cn/api/search/list'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "sfcx.neimenggu.chinatax.gov.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    @staticmethod
    def queue_name():
        return 'neimenggu'

    @property
    def headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            # 'Cookie': '_trs_uv=lv630vr7_343_fvxy',
            'Host': 'sfcx.neimenggu.chinatax.gov.cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    async def post_all_list(self, start_public_date: str, end_public_date: str = None):
        """
        post Queries list pages
        :param start_public_date:
        :param end_public_date:
        :return:
        """
        url = self.url
        if not end_public_date:
            end_public_date = start_public_date
        payload = {
            "articleNoNum": "",
            "articleNoYear": "",
            "author": "",
            "categoryId": 30492,
            "content": "",
            "endPublicDate": '',
            "page": 1,
            "plugin": {},
            "size": 15,
            "sortType": "",
            "startPublicDate": '',
            "tagIds": [],
            "title": "",
            "xlfw": "null"
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=self.headers)
        self.logger.info('get %s - %s', url, r.status_code)
        await self.parse_list_page(json_data=r.json(), start_date=start_public_date, end_date=end_public_date)

    async def parse_list_page(self, json_data, start_date, end_date):
        """
        解析 `/api/search/list` 列表数据

        解析数据示例：

        ```
            {
                "msg": "success",
                "status": 0,
                "data": {
                    "id": 30492,
                    "name": "按税种查询",
                    "parentId": 30481,
                    "code": "nmg_tax_search_gj_sz",
                    "pageSize": 1,
                    "sort": 0,
                    "count": 9128,
                    "attribute": {
                        "categoryId": "",
                        "title": "",
                        "keywords": "",
                        "description": "",
                        "extend": {
                            "withChild": "false",
                            "faguiType": "1",
                            "modelId": "fagui",
                            "level": "1",
                            "withParent": "false",
                            "tagIds": "996423",
                            "aggTagIds": "996423",
                            "withText": "false"
                        }
                    },
                    "contents": [
                        {
                            "id": "7185821459439161344",
                            "author": "工业和信息化部",
                            "categoryId": 3609,
                            "clicks": 20,
                            "description": "根据《中华人民共和国行政许可法》、《国务院对确需保留的行政审批项目设定行政许可的决定》、《财政部 税务总局 工业和信息化部 交通运输部关于节能 \n新能源车船享受车船税优惠政策的通知》(财税〔2018〕74号)、《工业和信息化部 财政部 国家税务总局关于调整享受车船税优惠的节能 \n新能源汽车产品技术要",
                            "dictionaryValues": "None",
                            "editor": "中华人民共和国工业和信息化部公告2024年第5号",
                            "expiryDate": "None",
                            "createDate": "None",
                            "hasFiles": "False",
                            "hasImages": "False",
                            "hasProducts": "False",
                            "modelId": "fagui",
                            "onlyUrl": "None",
                            "parentId": "None",
                            "publishDate": "2024-04-15",
                            "quoteContentId": "None",
                            "siteId": "90",
                            "tagIds": "None",
                            "text": "None",
                            "textHtml": "None",
                            "title": "《道路机动车辆生产企业及产品》（第381批）、《享受车船税减免优惠的节约能源 使用新能源汽车车型目录》（第六十批）、《减免车辆购置税的新能源汽车车型目录》（第四批）",
                            "url": "None",
                            "cover": "None",
                            "source": "None",
                            "sourceUrl": "https://www.miit.gov.cn/zwgk/zcwj/wjfb/gg/art/2024/art_5e5407eaa8a74ec89101e7501cdbf77f.html",
                            "extend": {
                                "sx_date_date": "2024-04-15",
                                "state_dictionary": "1",
                                "type_dictionary": "1"
                            },
                            "sort": 0,
                            "attribute": {}
                        },
                        {
                            "id": "7183270213901619200",
                            "author": "财政部 海关总署 税务总局",
                            "categoryId": 3609,
                            "clicks": 22,
                            "description": "内蒙古、辽宁、吉林、黑龙江、广西、云南、西藏、新疆等省(自治区)财政厅，新疆生产建设兵团财政局，国家税务总局内蒙古、辽宁、吉林、黑龙江、广西、云南、西藏、新疆等省(自治区)税务局，呼和浩特、满洲里、大连、长春、哈尔滨、南宁、昆明、拉萨、乌鲁木齐海关：为完善边境贸易支持政策，优化边民互市贸易多元化发展",
                            "dictionaryValues": "None",
                            "editor": "财关税〔2024〕7号",
                            "expiryDate": "None",
                            "createDate": "None",
                            "hasFiles": "False",
                            "hasImages": "False",
                            "hasProducts": "False",
                            "modelId": "fagui",
                            "onlyUrl": "None",
                            "parentId": "None",
                            "publishDate": "2024-04-08",
                            "quoteContentId": "None",
                            "siteId": "90",
                            "tagIds": "None",
                            "text": "None",
                            "textHtml": "None",
                            "title": "财政部 海关总署 税务总局关于边民互市贸易进出口商品不予免税清单的通知",
                            "url": "None",
                            "cover": "None",
                            "source": "None",
                            "sourceUrl": "http://gss.mof.gov.cn/gzdt/zhengcefabu/202404/t20240408_3932404.htm",
                            "extend": {
                                "sx_date_date": "2024-04-08",
                                "state_dictionary": "1",
                                "type_dictionary": "1"
                            },
                            "sort": 0,
                            "attribute": {}
                        }...
                    ],
                    "tags": [
                        {
                            "id": 6529064,
                            "name": "关税",
                            "searchCount": 950,
                            "sort": 5,
                            "path": "6529064",
                            "children": "None"
                        },
                        {
                            "id": 6528788,
                            "name": "车船税",
                            "searchCount": 154,
                            "sort": 10,
                            "path": "6528788",
                            "children": "None"
                        }...
                    ]
        }
        ```
        :param end_date:
        :param start_date:
        :param json_data:
        :return:
        """
        res = []
        self.logger.info('Parse  <内蒙古> - %s', json_data)
        contents = json_data.get('data').get('contents')
        filtered_data = [item for item in contents if start_date <= item["publishDate"].replace("-", "") <= end_date]
        for item in filtered_data:
            item_url = f'http://sfcx.neimenggu.chinatax.gov.cn/tax/detail?id={item.get("id")}&title=&content=&articleNoYear=&articleNoNum=&jiedutype=',
            async with httpx.AsyncClient() as client:
                respo = await client.get(item.get('sourceUrl'), headers=self.headers)

            self.logger.info('get %s - %s', item_url, respo.status_code)
            text_content = self.parse_text_contents(respo.text)
            res.append({
                'link': item_url,
                'title': item.get('title'),
                'editor': item.get('editor'),
                'state': '',
                'date': item.get('publishDate'),
                'tax_type': '',
                'text': text_content,
                'appendix': '',
                'related_documents': item.get('sourceUrl'),
            })
        print(json_data)

    def parse_text_contents(self, html_text: str):
        """
        parse text contents

        # //*[@class="detailContent"] 正文内容
        # 附件地址 https://www.miit.gov.cn/ `cms_files/filemanager/1226211233/attach/20243/ac168a7ee9694b84a17c6801bf0c2d47.doc`
        :param html_text:
        :return:
        """
        self.logger.info('parse text contents')
        html = etree.HTML(html_text)
        text = html.xpath('//*[@class="ccontent center"]/text()')
        return '\n'.join(text)
