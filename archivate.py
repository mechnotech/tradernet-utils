import os
import pathlib
import shutil
from datetime import datetime

import pytz


def time_now():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    msk_t = utc_time.astimezone(pytz.timezone("Europe/Moscow"))
    return msk_t


def is_file_exist(filename):
    if os.path.isfile(f'archives/{filename}.zip'):
        return filename + '-copy'
    return filename


def clean_up(name, dir_name):
    output_filename = is_file_exist(f'{name}-{str(time_now().date())}')

    shutil.make_archive(output_filename, 'zip', dir_name)
    shutil.move(f'./{output_filename}.zip',
                f'archives/{output_filename}.zip')
    cur_dir = pathlib.Path(dir_name)
    current_pattern = "*.txt"
    for currentFile in cur_dir.glob(current_pattern):
        os.remove(currentFile)


if __name__ == '__main__':
    clean_up('tickers', 'tickers_log')
