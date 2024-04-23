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
- appendix 附件（链接下载） 注: 多个链接时使用 ` /` 分号分割
- related documents 相关文件（链接） 注: 多个链接时使用 ` /` 分号分割

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

```bash
python .\src\crawlers_tax_policy_data\cmdline.py
Usage: cmdline.py [OPTIONS] COMMAND [ARGS]...

Options:
  -V, --version  Show version and exit.
  -v, --verbose  Get detailed output
  --help         Show this message and exit.

Commands:
  crawlers-gov  政府网站爬虫, 请使用 `crawlers_gov --help` 获取详细说明
```
```bash
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov --help

Usage: cmdline.py crawlers-gov [OPTIONS]

  政府网站爬虫, 请使用 `crawlers-gov --help` 获取详细说明

  下列是可提供的采集方案:  请使用 -c 或 --city 参数指定爬虫, 并在 config/settings `CRAWLERS_DATE`
  中设置需要采集的日期

  ----------------------------------------------------------------

  gov [中央人民政府](www.gov.cn/zhengce/xxgk/)

  ----------------------------------------------------------------

Options:
  -c, --city TEXT  选择要采集的网站  [default: gov]
  --help           Show this message and exit.
```

例如: 
```bash
# 采集 [中央人民政府](www.gov.cn/zhengce/xxgk/) 网站数据
python .\src\crawlers_tax_policy_data\cmdline.py crawlers-gov -c gov
```


