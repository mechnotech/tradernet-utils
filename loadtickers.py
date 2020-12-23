import logging
import time
from datetime import datetime
from json.decoder import JSONDecodeError

import pytz

from calc import day_result
from settings import (
    TRADE_START_HOUR,
    TRADE_STOP_HOUR,
    TRADING_DAYS,
    V_INFO,
    TOP_IDS,
    SLEEP_TIME,
    WAIT_TIME,
    CALC_START,
    CALC_STOP,
    CALC_HOLD_TIME,
    CHUNK_SIZE
)
from utils import get_ticker

logging.basicConfig(
    filename='tickers_log/status.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)


def time_now():
    utc_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    msk_t = utc_time.astimezone(pytz.timezone("Europe/Moscow"))
    return msk_t


def is_do():
    working_hours = range(TRADE_START_HOUR, TRADE_STOP_HOUR)
    working_days = TRADING_DAYS
    msk_t = time_now()
    if msk_t.isoweekday() in working_days and msk_t.hour in working_hours:
        return True
    return False


def is_do_calc():
    working_hours = range(CALC_START, CALC_STOP)
    working_days = TRADING_DAYS
    msk_t = time_now()
    if msk_t.isoweekday() in working_days and msk_t.hour in working_hours:
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


def save_files(chunck):
    filedata = {
        idf: open(
            f'tickers_log/{idf}.txt', 'a+', encoding='utf8'
        ) for idf in TOP_IDS
    }
    for name, f in filedata.items():
        block = ''
        for record in chunck.get(name):
            block += ','.join(record) + '\n'

        f.write(block)
        f.close()
    return


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
    ticker_d = {ids: [None] for ids in TOP_IDS}
    chunk_d = {ids: [] for ids in TOP_IDS}
    ch_count = 0
    logging.info(f'Запуск записи тикеров - {time_now()}')

    while True:
        if is_do_calc():
            logging.info('День завершен, приступаем к расчетам')
            day_result()
            logging.info('Расчеты окончены - см results, файлы перенесены')
            time.sleep(CALC_HOLD_TIME)

        if not is_do():
            logging.info('Не рабочее время!')
            time.sleep(WAIT_TIME)
            continue

        if len(chunk_d[TOP_IDS[0]]) > CHUNK_SIZE:
            save_files(chunk_d)
            logging.info(f'{ch_count} блоков записано')
            chunk_d.clear()
            ch_count += 1

        new_ticker = one_pass()

        # Если предыдущее значение отличается от текущего - добавляем в чанк
        for k, v in chunk_d.items():
            try:
                ex = v[-1][0]
            except IndexError:
                ex = False
            if ex != new_ticker.get(k)[0]:
                v.append(new_ticker.get(k))
