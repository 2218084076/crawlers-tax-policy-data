# crawlers-tax-policy-data

> Get the specified field data of public announcements in the government affairs platform

## Please check the development documentation before use [develop.md](docs%2Fdevelop.md)

> 针对 `财政部` www.mof.gov.cn
> 爬虫，由于三个页面解析逻辑通用，需通过 [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
> 中的 `MOF_URL_SUFFIX` 参数指定当个爬虫运行
>
> `四川省人民政府`  www.sc.gov.cn
> 爬虫任务执行顺序通过 [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml) 中 `SC_GOV` 参数配置

## 以提供的爬虫网站

- 爬虫管理器：[manage.py](src%2Fcrawlers_tax_policy_data%2Fmanage.py)

| Alias                | Spider Class                                                                                                              | Description                                                                     |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| gov                  | GovSpider               <br/>   [gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgov.py)                                | 中央人民政府                                                                          |
| sz-gov               | ShenZhengSpider         <br/>[shenzhen.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshenzhen.py)                         | 深圳市人民政府                                                                         |
| sh-gov               | ShangHaiGovSpider       <br/>[shanghai_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshanghai_gov.py)                 | 上海市人民政府                                                                         |
| zj-gov               | ZJSpider                <br/>[zhejiang_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fzhejiang_gov.py)                 | 浙江省人民政府                                                                         |
| gd-gov-latest-policy | GdGovLatestPolicySpider <br/>[gd_gov_latest_policy.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_latest_policy.py) | 广东省人民政府  文件库                                                                    |
| gd-gov-doc-lib       | GdGovDocLibSpider       <br/>[gd_gov_doc_lib.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_doc_lib.py)             | 广东省人民政府 最新政策                                                                    |
| gz-gov               | GzGovSpider             <br/>[gz_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgz_gov.py)                             | 广州市人民政府                                                                         |
| js-gov               | JsGovSpider             <br/>[js_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fjs_gov.py)                             | 江苏省人民政府                                                                         |
| bj-gov               | BjGovSpider             <br/>[bj_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fbj_gov.py)                             | 北京市人民政府                                                                         |
| sc-gov               | ScGovSpider             <br/> [sc_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsc_gov.py)                            | 四川省人民政府 `gfxwj`, `newzfwj`, `bmgfxwj` 三个网址的爬虫，请在 settings.yml 配置文件中 SC_GOV 参数确认 |
| safe                 | SafeSpider              <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 国家外汇管理局                                                                         |
| mof                  | MofSpider               <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 财政部                                                                             |
| csrc                 | CsrcSpider              <br/>[csrc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fcsrc.py)                                 | 证监会                                                                             |
| miit                 | MiitSpider              <br/>[miit.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fmiit.py)                                 | 工业和信息化部                                                                         |
| pbc                  | PbcSpider               <br/>[pbc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fpbc.py)                                   | 中国人民银行                                                                          |

[//]: # (| ndrc                 | NdrcSpider              |                                                                         |)
