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
    政府网站爬虫，请使用 `crawlers-gov --help` 获取详细说明

    下列是可提供的采集方案：
    请使用 -c 或 --city 参数指定爬虫，并在 config/settings `CRAWLERS_DATE` 中设置需要采集的日期

    ----------------------------------------------------------------

    gov
    [中央人民政府](www.gov.cn/zhengce/xxgk/)

    sz-gov
    [深圳政府在线](https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/szsfg/index.html)

    pudong-gov
    [上海市浦东新区人民政府](https://www.pudong.gov.cn/)
    ----------------------------------------------------------------
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawlers_factory(city).run())


@main.command()
def run_all():
    """
    并发执行所有爬虫实例
    """
    asyncio.run(all_crawlers())


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
