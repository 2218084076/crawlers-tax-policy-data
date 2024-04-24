# encoding:utf-8
import csv
import logging

logger = logging.getLogger(f'{__name__}')


def save_data(content: dict, file_path):
    """
    save data to local csv files
    :param file_path:
    :param content:
    :return:
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    header = ['链接', '标题', '文号', '状态', '发文日期', '税种', '正文', '附件', '相关文件/链接']
    write_header = not file_path.exists() or file_path.stat().st_size == 0

    with open(file_path, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(header)

        writer.writerow([
            content['link'],
            content['title'],
            content.get('editor'),
            content.get('state'),
            content['date'],
            content.get('tax_type'),
            content.get('text'),
            content.get('appendix'),
            content.get('related_documents'),
        ])
        logger.info('<%s> Write to file %s', content['title'], file_path)
