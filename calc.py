import json
import logging
import sys
import time
from datetime import datetime

import pytz

from archivate import clean_up

from settings import TOP_IDS, RISK_PCN

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


def percent_change(pair):
    res = 100 * (pair[1] - pair[0]) / pair[0]
    return round(res, 5)


def percent_price(price: float, is_ask: bool, my_perc):
    percent = price / 100 * my_perc
    if is_ask:
        return round(price - percent, 2)
    return round(price + percent, 2)


def get_block_paper(line, cash):
    """
    'SBER,261.45,56,624938,261.41,134,648207,0.01,0.01,1608558207'

    :param line: Входная строка файла с котировками
    :param cash: из какого объема считать
    :return:
    """
    ln = line.strip('\n')
    ln = ln.split(',')
    paper_price = float(ln[1])
    risk_sum = cash / 100 * RISK_PCN
    return int(risk_sum // paper_price)


def get_price_of_papers(line, paper):
    ln = line.strip('\n')
    ln = ln.split(',')
    paper_price = float(ln[4])
    return paper * paper_price


def calc_profit(ticker, my_perc):
    with open(f'tickers_log/{ticker}.txt', 'r') as f:
        lines = f.readlines()

    count = 0
    order_bye = 0
    order_sell = 0
    cash = 100000
    mem_cash = cash
    block = get_block_paper(line=lines[0], cash=cash)
    paper = 0
    count_b = 0
    count_s = 0
    for line in lines:
        ln = line.strip('\n')
        ln = ln.split(',')
        try:
            byd = float(ln[1])  # Большее - за сколько продают
            ask = float(ln[4])  # Меньшее - за сколько покупают
        except IndexError:
            logging.error(f'Ошибка в строке N:{count} файл {ticker}')
            continue

        if ask > byd:
            continue

        if order_bye:
            if byd <= order_bye:
                # print('---- BUY ----')
                paper += block
                cash -= order_bye * block
                prj_byd = percent_price(float(byd), is_ask=False,
                                        my_perc=my_perc)
                order_sell = prj_byd
                order_bye = 0
                count_b += 1

        if order_sell:
            if ask >= order_sell:
                # print('---- SELL ----')
                paper -= block
                cash += order_sell * block
                prj_ask = percent_price(float(ask), is_ask=True,
                                        my_perc=my_perc)
                order_bye = prj_ask
                order_sell = 0
                count_s += 1

        # начало торгового дня
        if not order_bye:
            if not order_sell:
                # print('---- START ----')
                prj_ask = percent_price(float(ask), is_ask=True,
                                        my_perc=my_perc)
                order_bye = prj_ask

        count += 1

        # min_step = ln[-3]
        # pair = percent_change((byd, ask))
        # proj_pair = percent_change((prj_byd, prj_ask))
        # disp = f'{prj_byd:7} <-- {byd:7}| {ask:7} --> {prj_ask:7}' \
        #        f' {pair:10} {proj_pair:14}   bye_ord -> {order_bye:7} ' \
        #        f' {order_sell:2} <- sell_ord | paper:{paper:3} ' \
        #        f'cash{round(cash,2):10}'
        # print(disp)

    # Если остались бумаги на конец
    paper_price = 0
    if paper:
        try:
            paper_price = round(get_price_of_papers(lines[-1], paper), 2)
        except IndexError:
            logging.error(f'Ошибка в строке N:{count} файл {ticker}')
            paper_price = -1

    income = round(cash - mem_cash, 2)

    # print(f' Акций {paper:3}'
    #       f'   наличных {cash:.2f} (+{paper_price} - стоимость акций)'
    #       f'   продаж {count_b:5}'
    #       f'   покупок {count_s}')

    return income, my_perc, paper, paper_price


def search_best_pcn(ticker):
    my_perc = 0.1
    max_perc = 2
    perc_step = 0.01
    result = []
    # Переменные для отслеживания периода без изменений
    no_change_limit = 15
    no_change_counter = 0
    old_cash = 0

    while my_perc <= max_perc:
        res = calc_profit(ticker, round(my_perc, 3))
        if not res:
            break

        # Если нет изменний - коэфф неактуальный, надо прервать цикл раньше
        if old_cash != res[0]:
            old_cash = res[0]
        else:
            no_change_counter += 1
        if no_change_counter >= no_change_limit:
            break

        result.append(res)
        sys.stdout.write(
            f'\rПоиск коэффициента для {ticker}: {my_perc:.2f} до {max_perc}')
        sys.stdout.flush()
        my_perc += perc_step
    print('\n')
    best_r = sorted(result)[-1]
    worst_r = sorted(result)[0]
    print(f'Лучший процент для {ticker}: {best_r[1]} -> {best_r[0]} руб')
    print(f'Худший процент для {ticker}: {worst_r[1]} -> {worst_r[0]} руб')
    return best_r[1], worst_r[1], result


def day_result():
    day_res = {}
    for ids in TOP_IDS:
        try:
            with open(f'tickers_log/{ids}.txt', 'r'):
                pass
        except FileNotFoundError:
            logging.error(f'Файла {ids}.txt не существует!')
            continue

        best, worst, raw_data = search_best_pcn(ids)
        day_res[ids] = (best, worst, raw_data)
        load = day_res.get(ids)
        with open(f'results/{ids}.log', 'a+') as f:
            f.write(str(time_now().date()) + '|' + json.dumps(load) + '\n')

    clean_up('tickers', 'tickers_log')
    return day_res


if __name__ == '__main__':
    start_time = time.time()
    print(day_result())

    # calc_profit('SBER', round(0.41, 3))
    print("--- %s seconds ---" % (time.time() - start_time))
