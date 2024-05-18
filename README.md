- [crawlers-tax-policy-data](#crawlers-tax-policy-data)
    - [Please check the development documentation before use develop.md](#please-check-the-development-documentation-before-use-developmd)
    - [财政部-mof.gov.cn 爬虫说明](#%E8%B4%A2%E6%94%BF%E9%83%A8-mofgovcn-%E7%88%AC%E8%99%AB%E8%AF%B4%E6%98%8E)
    - [四川省人民政府-sc.gov.cn 爬虫说明](#%E5%9B%9B%E5%B7%9D%E7%9C%81%E4%BA%BA%E6%B0%91%E6%94%BF%E5%BA%9C-scgovcn-%E7%88%AC%E8%99%AB%E8%AF%B4%E6%98%8E)
    - [已提供的爬虫网站](#%E5%B7%B2%E6%8F%90%E4%BE%9B%E7%9A%84%E7%88%AC%E8%99%AB%E7%BD%91%E7%AB%99)

# crawlers-tax-policy-data

> Get the specified field data of public announcements in the government affairs platform

## Please check the development documentation before use [develop.md](docs%2Fdevelop.md)

## 财政部-mof.gov.cn 爬虫说明

> 针对 `财政部` www.mof.gov.cn
> 爬虫，由于三个页面解析逻辑通用，需通过 [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
> 中的 `MOF_URL_SUFFIX` 参数指定当个爬虫运行

## 四川省人民政府-sc.gov.cn 爬虫说明

> `四川省人民政府`  www.sc.gov.cn
> 爬虫任务执行顺序通过 [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml) 中 `SC_GOV` 参数配置

## 已提供的爬虫网站

- 爬虫管理器：[manage.py](src%2Fcrawlers_tax_policy_data%2Fmanage.py)

| Alias                | Spider Class                                                                                                              | Description                                                                                                                                                                                            |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| gov                  | GovSpider               <br/>   [gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgov.py)                                | 中央人民政府                                                                                                                                                                                                 |
| sz-gov               | ShenZhengSpider         <br/>[shenzhen.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshenzhen.py)                         | 深圳市人民政府                                                                                                                                                                                                |
| sh-gov               | ShangHaiGovSpider       <br/>[shanghai_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshanghai_gov.py)                 | 上海市人民政府                                                                                                                                                                                                |
| zj-gov               | ZJSpider                <br/>[zhejiang_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fzhejiang_gov.py)                 | 浙江省人民政府                                                                                                                                                                                                |
| gd-gov-latest-policy | GdGovLatestPolicySpider <br/>[gd_gov_latest_policy.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_latest_policy.py) | 广东省人民政府  文件库                                                                                                                                                                                           |
| gd-gov-doc-lib       | GdGovDocLibSpider       <br/>[gd_gov_doc_lib.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_doc_lib.py)             | 广东省人民政府 最新政策                                                                                                                                                                                           |
| gz-gov               | GzGovSpider             <br/>[gz_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgz_gov.py)                             | 广州市人民政府                                                                                                                                                                                                |
| js-gov               | JsGovSpider             <br/>[js_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fjs_gov.py)                             | 江苏省人民政府                                                                                                                                                                                                |
| bj-gov               | BjGovSpider             <br/>[bj_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fbj_gov.py)                             | 北京市人民政府                                                                                                                                                                                                |
| sc-gov               | ScGovSpider             <br/> [sc_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsc_gov.py)                            | 四川省人民政府 <br/>`gfxwj`, `newzfwj`, `bmgfxwj` 三个网址的爬虫，请在 settings.yml 配置文件中 SC_GOV 参数确认                                                                                                                   |
| safe                 | SafeSpider              <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 国家外汇管理局                                                                                                                                                                                                |
| mof                  | MofSpider               <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 财政部                                                                                                                                                                                                    |
| csrc                 | CsrcSpider              <br/>[csrc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fcsrc.py)                                 | 证监会                                                                                                                                                                                                    |
| miit                 | MiitSpider              <br/>[miit.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fmiit.py)                                 | 工业和信息化部                                                                                                                                                                                                |
| pbc                  | PbcSpider               <br/>[pbc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fpbc.py)                                   | 中国人民银行                                                                                                                                                                                                 |
| ndrc                 | NdrcSpider              <br/>[ndrc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fndrc.py)                                 | 国家发改委                                                                                                                                                                                                  |
| cbirc                | CbircSpider<br/>  [cbirc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fcbirc.py)                                          | 银保监会  <br/> http://www.cbirc.gov.cn/cn/view/pages/zhengwuxinxi/zhengfuxinxi.html?signIndex=4#1 <br/> 分类采集：<br/>- 行政规范性文件  tag 标签位置 //span[@item="4215"]<br/>- 其他文件       tag 标签位置 //span[@item="4216"] |
| samr                 | SamrSpider<br/>[samr.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsamr.py)                                               | 市场监督管理总局                                                                                                                                                                                               |
| nmpa                 | NmpaSpider<br/>[nmpa.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fnmpa.py)                                               | 国家药监局    <br/>https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/index.html  工作文件<br/>https://www.nmpa.gov.cn/xxgk/fgwj/xzhgfxwj/index.html  行政规范性文件                                                               |
| shui5                | ShuiWuSpider<br/>[shui5.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshui5.py)                                           | 税屋         <br/>https://www.shui5.cn/article/DiFangCaiShuiFaGui/ 税屋 > 地方法规<br/>https://www.shui5.cn/article/NianDuCaiShuiFaGui/ 税屋 > 中央法规                                                                        |
