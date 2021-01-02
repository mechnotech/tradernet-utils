import logging
import time
from datetime import datetime
from json.decoder import JSONDecodeError

import pytz

from calc import day_result
from settings import (
    V_INFO,
    TOP_IDS,
    SLEEP_TIME,
    WAIT_TIME,
    CHUNK_SIZE,
)
from utils import get_ticker, is_do


logging.basicConfig(
    filename='tickers_log/status.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)


class Chunk:

    @property
    def is_empty(self):
        for i in self.tickers:
            if i:
                return False
        return True

    @property
    def len(self):
        for i in self.tickers.values():
            return len(i)

    def __init__(self):
        self.tickers = None
        self.clear()
        self.blocks = 0

    def add(self, val):
        for k, v in val.items():
            try:
                ex = self.tickers.get(k)[-1][0]
            except IndexError:
                ex = False
            # Если предыдущее значение отличается от текущего
            # - добавляем в чанк
            if ex != v[0]:
                self.tickers[k].append(v)

    def clear(self):
        self.tickers = {ids: [] for ids in TOP_IDS}
        return

    def save(self):
        if not self.is_empty:
            file_data = {
                idf: open(
                    f'tickers_log/{idf}.txt', 'a+', encoding='utf8'
                ) for idf in TOP_IDS
            }
            for name, f in file_data.items():
                block = ''
                for record in self.tickers.get(name):
                    block += ','.join(record) + '\n'

                f.write(block)
                f.close()
            self.blocks += 1
            self.clear()


def time_now():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    msk_t = utc_time.astimezone(pytz.timezone("Europe/Moscow"))
    return msk_t


def is_do_calc(flag):
    if not flag:
        return False
    if not is_do():
        return True
    return False


def extract(d):
    result = []
    for i in V_INFO:
        result.append(str(d.get(i, None)))
    result = ','.join(result)
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    ts = (str(timestamp).split('.')[0])
    return [result, ts]


def one_pass():
    new = {}
    for ids in TOP_IDS:
        try:
            info = get_ticker(ids)
        except JSONDecodeError:
            verdict = f'Ошибка декодирования JSON для {ids}'
            logging.error(verdict)
            continue

        val_info = extract(info)
        ticker = info.get('c')
        new[ticker] = val_info
        time.sleep(SLEEP_TIME)
    return new


if __name__ == '__main__':
    chunk_d = Chunk()
    logging.info(f'Запуск записи тикеров - {time_now()}')
    calc_flag = True

    while True:
        if is_do_calc(calc_flag):
            logging.info('День завершен, приступаем к расчетам')
            day_result()
            logging.info('Расчеты окончены - см results, файлы перенесены')
            calc_flag = False

        if not is_do():
            logging.info('Не рабочее время!')
            time.sleep(WAIT_TIME)
            continue

        calc_flag = True

        new_tickers = one_pass()
        chunk_d.add(new_tickers)

        if chunk_d.len > CHUNK_SIZE:
            chunk_d.save()
            logging.info(f'{chunk_d.blocks} тикеров записано')
