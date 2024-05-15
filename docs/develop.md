- [开发文档](#%E5%BC%80%E5%8F%91%E6%96%87%E6%A1%A3)
    - [需求](#%E9%9C%80%E6%B1%82)
        - [采集数据格式](#%E9%87%87%E9%9B%86%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F)
    - [部署指南](#%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)
        - [依赖管理](#%E4%BE%9D%E8%B5%96%E7%AE%A1%E7%90%86)
        - [动态配置](#%E5%8A%A8%E6%80%81%E9%85%8D%E7%BD%AE)
    - [使用指南](#%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)
    - [已提供的爬虫网站](#%E5%B7%B2%E6%8F%90%E4%BE%9B%E7%9A%84%E7%88%AC%E8%99%AB%E7%BD%91%E7%AB%99)

# 开发文档

## 需求

获取政务平台中公开公告指定字段数据

### 采集数据格式

```json
{
  "link": "",
  "title": "",
  "editor": "",
  "state": "",
  "date": "",
  "tax_type": "",
  "text": "",
  "appendix": "",
  "related_documents": ""
}
```

- link 链接
- title 标题
- editor 文号
- state 状态
- issue date 发文日期
- tax type 税种
- text 正文
- appendix 附件（链接下载）
- related documents 相关文件（链接）

## 部署指南

### 依赖管理

> 本项目使用 `poetry` 进行依赖管理
>
> 其中依赖都记录在 [pyproject.toml](..%2Fpyproject.toml) 文件中
>
>在项目根目录中执行
>
> ```bash
> # 在系统环境中安装  `poetry` 库
> pip install -U poetry 
> # 安装所有依赖
> poetry install
> # 进入 poetry 创建的虚拟 python 环境
> poetry shell
> # 注: 本项目依赖中使用了 playwright 浏览器自动化工具, 依赖 playwright 浏览器驱动, 
> # 必要时需手动 `playwright install` 安装浏览器驱动
> ``` 

- 到此为止, 项目所有所需依赖全部安装完毕

### 动态配置

> 本项目使用 `dynaconf` 来实现动态配置

本地部署时, 建议使用使用本地配置, 替换项目默认配置,
配置方法如下:

- 可按照 [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  文件格式, 在其同级（即与 [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  同级路径）创建 `settings.local.yml` 文件
- `settings.local.yml` 文件会自动替换掉 [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  中默认配置, 并且会被 `git ignore` 不会被 git 提交到远程仓库
-

## 使用指南

- **运行爬虫前请确认 [settings.yml](..%2Fsrc%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml) 配置文件的 `START_DATE`
  和 `END_DATE` 参数是否为您想要采集的日期**
- 默认 `START_DATE` 和 `END_DATE` 两个参数为空, 即为从当前日期开始采集,
  参数说明如下：
- 针对 `财政部` www.mof.gov.cn
  爬虫，由于三个页面解析逻辑通用，需通过 [settings.yml](src%2Fcrawlers_tax_policy_data%2Fconfig%2Fsettings.yml)
  中的 `MOF_URL_SUFFIX` 参数指定当个爬虫运行
    - 其要想单单独运行一个网站，则需注释掉其他两个网站的配置，全部打开时，爬虫会依次采集指定日期范围内数据。
    - ```yaml
       MOF_URL_SUFFIX:
          财政文告: "/caizhengwengao/index"  # 财政文告
          财政部令: "/bulinggonggao/czbl/index"  # 财政部令
          财政部公告: "/bulinggonggao/czbgg/index"  # 财政部公告
    ```

```yaml
# 需要采集的日期，
# 注：日期格式要按照 `年月日` 的形式 例如 `20240409` 程序中已定义了固定的 date 解析逻辑
# 错误示范：2024-01-12、2024年1月2日
# 要想指定采集某天单日的数据，则只需指定 start_date 或者 end_date
# start_date 和 end_date 都设置为空，则自动采集当前日期内数据
```

```bash
python .\src\crawlers_tax_policy_data\cmdline.py
Usage: cmdline.py [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version  Show version and exit.
  -v, --verbose  Get detailed output
  --help         Show this message and exit.

Commands:
  crawlers-gov  政府网站爬虫, 请使用 `crawlers-gov --help` 获取详细说明
  run-all       逐一运行每个爬虫, 请在配置文件中确认采集日期! 

```

```bash
Usage: cmdline.py crawlers-gov [OPTIONS]

  政府网站爬虫，请使用 `crawlers-gov --help` 获取详细说明

  下列是可提供的采集方案： 请使用 -c 或 --city 参数指定爬虫，

  并在 config/settings `START_DATE`和`END_DATE` 中确认需要采集的日期，默认采集当日的数据

  ----------------------------------------------------------------
  gov [中央人民政府](www.gov.cn)

  sz-gov [深圳政府在线](www.sz.gov.cn)

  sh-gov [上海市人民政府](www.shanghai.gov.cn)

  zj-gov [浙江省人民政府](www.zj.gov.cn)

  gd-gov-latest-policy [广东省政府 > 最新政策](www.gd.gov.cn/gdywdt)

  gd-gov-doc-lib [广东省政府 > 文件库](www.gd.gov.cn/zwgk/wjk/qbwj/)

  gz-gov [广州市行政规范性文件统一发布平台](www.gz.gov.cn/gfxwj/)

  js-gov [江苏省人民政府](jiangsu.gov.cn)

  bj-gov [北京市人民政府](beijing.gov.cn)

  sc-gov [四川省人民政府](sc.gov.cn)

  safe [国家外汇管理局](safe.gov.cn)

  mof [财政部 财政文告;财政部令;财政部公告](mof.gov.cn)
  
  csrc [证监会](www.csrc.gov.cn)

  miit [工业和信息化部](www.miit.gov.cn)

  pbc [中国人民银行](www.pbc.gov.cn)

  ndrc [国家发改委](www.ndrc.gov.cn)
  
  cbirc [银保监会](www.cbirc.gov.cn)

  samr [市场监督管理总局](www.samr.gov.cn)

  ----------------------------------------------------------------

Options:
  -c, --city TEXT  选择要采集的网站  [default: gov]
  --help           Show this message and exit.
```

例如:

```bash
# 采集 [中央人民政府](www.gov.cn/zhengce/xxgk/) 网站数据
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov -c gov
# 逐一运行每个爬虫
python .\src\crawlers_tax_policy_data\cmdline.py run-all
```

## 已提供的爬虫网站

- 爬虫管理器：[manage.py](src%2Fcrawlers_tax_policy_data%2Fmanage.py)

| Alias                | Spider Class                                                                                                              | Description                                                                          |
|:---------------------|:--------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|
| gov                  | GovSpider               <br/>   [gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgov.py)                                | 中央人民政府                                                                               |
| sz-gov               | ShenZhengSpider         <br/>[shenzhen.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshenzhen.py)                         | 深圳市人民政府                                                                              |
| sh-gov               | ShangHaiGovSpider       <br/>[shanghai_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fshanghai_gov.py)                 | 上海市人民政府                                                                              |
| zj-gov               | ZJSpider                <br/>[zhejiang_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fzhejiang_gov.py)                 | 浙江省人民政府                                                                              |
| gd-gov-latest-policy | GdGovLatestPolicySpider <br/>[gd_gov_latest_policy.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_latest_policy.py) | 广东省人民政府  文件库                                                                         |
| gd-gov-doc-lib       | GdGovDocLibSpider       <br/>[gd_gov_doc_lib.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgd_gov_doc_lib.py)             | 广东省人民政府 最新政策                                                                         |
| gz-gov               | GzGovSpider             <br/>[gz_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fgz_gov.py)                             | 广州市人民政府                                                                              |
| js-gov               | JsGovSpider             <br/>[js_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fjs_gov.py)                             | 江苏省人民政府                                                                              |
| bj-gov               | BjGovSpider             <br/>[bj_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fbj_gov.py)                             | 北京市人民政府                                                                              |
| sc-gov               | ScGovSpider             <br/> [sc_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsc_gov.py)                            | 四川省人民政府 <br/>`gfxwj`, `newzfwj`, `bmgfxwj` 三个网址的爬虫，请在 settings.yml 配置文件中 SC_GOV 参数确认 |
| safe                 | SafeSpider              <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 国家外汇管理局                                                                              |
| mof                  | MofSpider               <br/>[safe_gov.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsafe_gov.py)                         | 财政部                                                                                  |
| csrc                 | CsrcSpider              <br/>[csrc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fcsrc.py)                                 | 证监会                                                                                  |
| miit                 | MiitSpider              <br/>[miit.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fmiit.py)                                 | 工业和信息化部                                                                              |
| pbc                  | PbcSpider               <br/>[pbc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fpbc.py)                                   | 中国人民银行                                                                               |
| ndrc                 | NdrcSpider              <br/>[ndrc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fndrc.py)                                 | 国家发改委                                                                                |
| cbirc                | CbircSpider<br/>  [cbirc.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fcbirc.py)                                          | 银保监会                                                                                 |
| samr                 | SamrSpider<br/>[samr.py](src%2Fcrawlers_tax_policy_data%2Fspider%2Fsamr.py)                                               | 市场监督管理总局                                                                             |
