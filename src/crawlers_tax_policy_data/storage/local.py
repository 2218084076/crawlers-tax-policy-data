import csv


def save_data(content: dict, file_path):
    """
    save data to local csv files
    :param file_path:
    :param content:
    :return:
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([content['link'], content['title'], content['editor'], content['date'], content['text']])
