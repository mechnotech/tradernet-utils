import json
import os
import urllib.parse
from datetime import datetime

import requests
from dotenv import load_dotenv

import PublicApiClient as NtApi
from settings import MY_STOCKS

load_dotenv()
URL = 'https://tradernet.ru/securities/export/'
pub_ = os.getenv('TN_PUB_KEY')
sec_ = os.getenv('TN_PRIVATE_KEY')

res = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V2)


def get_ticker(ticker, sup=False):
    cmd_ = 'getSecurityInfo'
    param_ = {
        'ticker': ticker,
        'sup': sup
    }
    res = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V1)
    return json.loads(res.sendRequest(cmd_, param_).content)


def get_top():
    cmd_ = 'getTopSecurities'
    param_ = {
        'type': 'stocks',
        'exchange': 'russia',
        'gainers': 0,
        'limit': 10
    }
    res = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V1)
    return res.sendRequest(cmd_, param_).content.decode("utf-8")


def get_tickers(tickers: list, params: list = None) -> dict:
    """
    Получение котировки(ок)
    :param tickers: Список тикеров
    :param params: Список параметров (см description.txt)
    :return:
    """

    if not params:
        params = 'ltp+ltt+bbp+chg'
    else:
        params = '+'.join(params)

    payload = {
        'params': params,
        'tickers': '+'.join(tickers),
    }
    payload_str = urllib.parse.urlencode(payload, safe='+')
    res = requests.get(URL, params=payload_str)
    return json.loads(res.content)


def is_do():
    """ Открыт ли рынок """
    cmd_ = 'getMarketStatus'
    param_ = {
        'market': MY_STOCKS,
        # 'mode': "demo",
    }
    req = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V1)
    response = json.loads(req.sendRequest(cmd_, param_).content)
    try:
        result = response.get('result')
        op = result['markets']['m'][0].get('s')
        if result:
            return False if op == 'CLOSE' else True
    except KeyError:
        return False


def get_history(
        tickers: str,
        time_frame: int,
        date_from: str,
        date_to: str) -> dict:
    """
    :param tickers: Тикер или тикеры через запятую "SBER,GAZP"
    :param time_frame Свеча в минутах 1, 10, 60 ...
    :param date_from: С какой даты "15.08.2020 00:00"
    :param date_to: По какую дату
    :return Dict:
    """

    cmd_ = 'getHloc'
    params_ = {
        'id': tickers,
        'count': -1,
        'timeframe': time_frame,
        'date_from': date_from,
        'date_to': date_to,
        'intervalMode': 'ClosedRay'
    }

    req = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V1)
    return json.loads(req.sendRequest(cmd_, params_).content)


if __name__ == '__main__':
    # Получить ТОП-10 торгуемых get_top()
    TOP_IDS = ["SBER", "GAZP", "AFKS", "AFLT", "VTBR", "MAIL", "ALRS", "LKOH",
               "TATN", "MAGN"]

    # Получить один тикер
    print(get_ticker('SBER'))

    # Получить котировки по несколкьим тикерам через GET
    print(get_tickers(TOP_IDS))

    # Исторические данные: свечи, объемы, по тикерам
    tickers = ','.join(TOP_IDS)
    frame = 60
    start = '14.12.2020'
    finish = '15.12.2020'
    res = get_history(tickers, frame, start, finish)
    history = res.get('hloc')
    timest = res.get('xSeries').get('GAZP')
    for key, value in history.items():
        print(key)
        for i in range(len(value)):
            v = value[i]
            t = datetime.fromtimestamp(timest[i])
            print(f'{str(v):40}  {str(t):50}')
        print(len(value))
    print(type(is_do()), is_do())
