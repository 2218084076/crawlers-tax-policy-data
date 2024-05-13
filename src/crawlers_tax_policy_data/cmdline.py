# encoding: utf-8
"""
Cmdline.
"""
import asyncio

import click

from crawlers_tax_policy_data import __version__
from crawlers_tax_policy_data.config import settings
from crawlers_tax_policy_data.manage import all_crawlers, crawlers_factory
from crawlers_tax_policy_data.utils.log import init_log

init_log()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-V', '--version', is_flag=True, help='Show version and exit.')
@click.option('-v', '--verbose', is_flag=True, help='Get detailed output')
def main(ctx, version, verbose):
    """"""
    if version:
        click.echo(__version__)
    elif verbose:
        settings.set('VERBOSE', verbose)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.option('-c', '--city', default='gov', show_default=True, help='选择要采集的网站')
def crawlers_gov(city):
    """
    政府网站爬虫, 请使用 `crawlers-gov --help` 获取详细说明

    下列是可提供的采集方案：
    请使用 -c 或 --city 参数指定爬虫，

    并在 config/settings `START_DATE`和`END_DATE` 中确认需要采集的日期，默认采集当日的数据

    ----------------------------------------------------------------

    gov
    [中央人民政府](www.gov.cn)

    sz-gov
    [深圳政府在线](www.sz.gov.cn)

    sh-gov
    [上海市人民政府](www.shanghai.gov.cn)

    zj-gov
    [浙江省人民政府](www.zj.gov.cn)

    gd-gov-latest-policy
    [广东省政府 > 最新政策](www.gd.gov.cn/gdywdt)

    gd-gov-doc-lib
    [广东省政府 > 文件库](www.gd.gov.cn/zwgk/wjk/qbwj/)

    gz-gov
    [广州市行政规范性文件统一发布平台](www.gz.gov.cn/gfxwj/)

    js-gov
    [江苏省人民政府](jiangsu.gov.cn)

    bj-gov
    [北京市人民政府](beijing.gov.cn)

    sc-gov
    [四川省人民政府](sc.gov.cn)

    safe
    [国家外汇管理局](safe.gov.cn)

    mof
    [财政部 财政文告;财政部令;财政部公告](mof.gov.cn)

    csrc
    [证监会](www.csrc.gov.cn)

    miit
    [工业和信息化部](www.miit.gov.cn)

    pbc
    [中国人民银行](www.pbc.gov.cn)

    ndrc
    [国家发改委](www.ndrc.gov.cn)
    ----------------------------------------------------------------
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawlers_factory(city).run())


@main.command()
def run_all():
    """
    逐一运行每个爬虫, 请在配置文件中确认采集日期！
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(all_crawlers())


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
